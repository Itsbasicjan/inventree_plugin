# meinplugin/models.py
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings # To potentially get the User model if needed (but prefer InvenTreeUser)

# InvenTree models needed for ForeignKeys
from company.models import Company
from stock.models import StockItem
# Use InvenTree's custom user model proxy for consistency
from InvenTree.models import InvenTreeUser


class Loan(models.Model):
    """
    Represents a loan transaction, potentially involving multiple items.
    """

    class LoanStatus(models.TextChoices):
        """Defines the possible states of a loan."""
        PENDING = 'PENDING', _('Pending')       # Loan created, items not yet issued/moved
        ACTIVE = 'ACTIVE', _('Active')         # At least one item issued / on loan
        OVERDUE = 'OVERDUE', _('Overdue')       # Past due date, items not fully returned
        RETURNED = 'RETURNED', _('Returned')     # All items returned
        CANCELLED = 'CANCELLED', _('Cancelled')   # Loan cancelled before activation

    # Customer receiving the loan (links to InvenTree's Company model)
    customer = models.ForeignKey(
        Company,
        on_delete=models.PROTECT, # Prevent deleting customer if active loans exist
        limit_choices_to={'is_customer': True}, # Ensure it's a customer company
        related_name='loans_received', # How to access loans from a Company instance
        verbose_name=_('Customer')
    )

    # Date/Time when the loan record was initiated
    loan_date = models.DateTimeField(
        auto_now_add=True, # Set automatically on creation
        verbose_name=_('Loan Date')
    )

    # Expected return date for the loan
    due_date = models.DateField(
        verbose_name=_('Due Date')
    )

    # Actual date when all items of the loan were returned
    return_date = models.DateField(
        null=True, blank=True, # Null until fully returned
        verbose_name=_('Actual Return Date')
    )

    # Current status of the overall loan
    status = models.CharField(
        max_length=20,
        choices=LoanStatus.choices,
        default=LoanStatus.PENDING,
        verbose_name=_('Status')
    )

    # Optional reference identifier (e.g., order number, request ID)
    reference = models.CharField(
        max_length=100, blank=True,
        verbose_name=_('Reference / Order ID'),
        help_text=_('Optional reference for this loan')
    )

    # General notes about the loan transaction
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )

    # User who created the loan record in InvenTree
    created_by = models.ForeignKey(
       InvenTreeUser,
       on_delete=models.SET_NULL, # Keep loan record if user is deleted
       null=True, blank=True,
       related_name='loans_created', # How to access loans created by a user
       verbose_name=_('Created By')
    )

    # Timestamp of the last modification to the loan record
    updated_at = models.DateTimeField(
        auto_now=True, # Update automatically on save
        null=True, # Allows null initially
        verbose_name=_('Last Updated')
    )


    def __str__(self):
        """String representation of the Loan model."""
        return _("Loan {pk} to {customer}").format(pk=self.pk, customer=self.customer.name)

    def get_absolute_url(self):
        """Returns the URL to view the detail page for this loan."""
        # Assumes a URL named 'loan_detail' exists within the 'loan' namespace (plugin slug)
        return reverse('plugin:loan:loan_detail', kwargs={'pk': self.pk})

    @property
    def is_overdue(self):
        """Checks if the loan is currently active and past its due date."""
        from datetime import date
        # A loan is overdue if it's ACTIVE and the due date is in the past
        return self.status == self.LoanStatus.ACTIVE and self.due_date < date.today()


class LoanedItem(models.Model):
    """
    Represents an individual StockItem that is part of a specific Loan.
    """

    class ItemStatus(models.TextChoices):
        """Defines the status of a specific item within a loan."""
        PENDING = 'PENDING', _('Pending Issue') # Item added to loan, not yet physically moved
        ON_LOAN = 'ON_LOAN', _('On Loan')      # Item physically moved/issued to loan location
        RETURNED = 'RETURNED', _('Returned')    # Item physically returned from loan location
        # Could add more statuses like 'LOST', 'DAMAGED' if needed

    # Link back to the parent Loan transaction
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE, # If the Loan is deleted, associated LoanedItem records are also deleted
        related_name='items', # How to access items from a Loan instance (loan.items.all())
        verbose_name=_('Loan')
    )

    # The specific StockItem being loaned
    stock_item = models.ForeignKey(
        StockItem,
        on_delete=models.PROTECT, # Prevent deletion of StockItem if it's part of a loan record
        related_name='loan_records', # How to access loan history from a StockItem instance
        # Initially focus on serialized items for simplicity and better tracking
        limit_choices_to={'serialized': True},
        verbose_name=_('Stock Item')
    )

    # Note: Quantity is implicitly 1 for serialized items.
    # If supporting non-serialized items, a quantity field would be needed here:
    # quantity = models.DecimalField(max_digits=10, decimal_places=5, validators=[MinValueValidator(0.00001)], default=1, verbose_name=_('Quantity'))

    # Status of this specific item within the loan process
    status = models.CharField(
        max_length=20,
        choices=ItemStatus.choices,
        default=ItemStatus.PENDING,
        verbose_name=_('Item Status')
    )

    # Optional: Could add fields for condition tracking if needed
    # condition_notes_out = models.TextField(blank=True, verbose_name=_('Condition Notes (Out)'))
    # condition_notes_returned = models.TextField(blank=True, verbose_name=_('Condition Notes (Returned)'))


    def __str__(self):
        """String representation of the LoanedItem model."""
        return _("{item} on Loan {loan_pk}").format(item=self.stock_item, loan_pk=self.loan.pk)

    # Ensure that a specific StockItem is only actively on loan once at a time
    class Meta:
        unique_together = [
            # A StockItem can only be linked once to a Loan that is NOT returned/cancelled
            # Note: This constraint might need adjustment depending on exact workflow for PENDING items
            # ('stock_item', 'loan'), # Basic uniqueness if needed, but status matters more
        ]
        verbose_name = _('Loaned Item')
        verbose_name_plural = _('Loaned Items')
# meinplugin/models.py
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings # To get the User model

# InvenTree models needed for ForeignKeys
from company.models import Company
from stock.models import StockItem, StockLocation
from InvenTree.models import InvenTreeUser  # Get User model cleanly


class Loan(models.Model):
    """Represents a loan transaction."""

    class LoanStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')       # Loan created, items not yet issued
        ACTIVE = 'ACTIVE', _('Active')         # Items issued / on loan
        OVERDUE = 'OVERDUE', _('Overdue')       # Past due date, items not returned
        RETURNED = 'RETURNED', _('Returned')     # All items returned
        CANCELLED = 'CANCELLED', _('Cancelled')   # Loan cancelled before issue

    customer = models.ForeignKey(
        Company,
        on_delete=models.PROTECT, # Prevent deleting customer if loans exist
        limit_choices_to={'is_customer': True},
        related_name='loans',
        verbose_name=_('Customer')
    )

    loan_date = models.DateTimeField(
        auto_now_add=True, # Automatically set when created
        verbose_name=_('Loan Date')
    )

    due_date = models.DateField(
        verbose_name=_('Due Date')
    )

    return_date = models.DateField(
        null=True, blank=True,
        verbose_name=_('Actual Return Date')
    )

    status = models.CharField(
        max_length=20,
        choices=LoanStatus.choices,
        default=LoanStatus.PENDING,
        verbose_name=_('Status')
    )

    reference = models.CharField(
        max_length=100, blank=True,
        verbose_name=_('Reference / Order ID'),
        help_text=_('Optional reference for this loan')
    )

    notes = models.TextField(blank=True, verbose_name=_('Notes'))

    # Use InvenTree's recommended way to link to User
    created_by = models.ForeignKey(
       InvenTreeUser, on_delete=models.SET_NULL, null=True, blank=True,
       related_name='+', verbose_name=_('Created By')
    )

    # Last modification timestamp
    updated_at = models.DateTimeField(auto_now=True, null=True)


    def __str__(self):
        return f"Loan {self.pk} to {self.customer.name} due {self.due_date}"

    def get_absolute_url(self):
        # Assumes we will have a URL named 'loan_detail' in our plugin's urls.py
        # Requires plugin slug 'meinplugin'
        return reverse('plugin:meinplugin:loan_detail', kwargs={'pk': self.pk})

    @property
    def is_overdue(self):
        """Check if the loan is overdue."""
        from datetime import date
        # Check if status is ACTIVE and due_date is in the past
        return self.status == self.LoanStatus.ACTIVE and self.due_date < date.today()


class LoanedItem(models.Model):
    """An individual StockItem associated with a Loan."""

    class ItemStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending Issue') # Item added to loan, not yet physically moved
        ON_LOAN = 'ON_LOAN', _('On Loan')      # Item physically moved/issued
        RETURNED = 'RETURNED', _('Returned')    # Item physically returned
        # Could add more statuses like 'DAMAGED', 'LOST' etc. later

    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE, # If Loan is deleted, delete associated items
        related_name='items',
        verbose_name=_('Loan')
    )

    stock_item = models.ForeignKey(
        StockItem,
        on_delete=models.PROTECT, # Protect the StockItem from deletion if on loan
        related_name='loans', # Allows finding loans from a StockItem
        limit_choices_to={'serialized': True}, # IMPORTANT: Initially focus on serialized items
        verbose_name=_('Stock Item')
    )

    # Quantity is implicitly 1 for serialized items, but could be added for non-serialized
    # quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantity'))

    status = models.CharField(
        max_length=20,
        choices=ItemStatus.choices,
        default=ItemStatus.PENDING,
        verbose_name=_('Item Status')
    )

    # Could add fields like 'condition_notes_out', 'condition_notes_returned'

    def __str__(self):
        return f"{self.stock_item} on Loan {self.loan.pk}"
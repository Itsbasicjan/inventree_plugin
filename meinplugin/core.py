# meinplugin/core.py

# Standard Django imports
from django.http import HttpResponse
from django.urls import path, include # include needed for separate urls.py
from django.utils.translation import gettext_lazy as _

# InvenTree plugin imports
from plugin import InvenTreePlugin
from plugin.mixins import (NavigationMixin, ScheduleMixin, SettingsMixin,
                           UrlsMixin, UserInterfaceMixin)

# Import plugin's models and version
from . import PLUGIN_VERSION
from stock.models import StockLocation # Needed for Setting model choice

# Die Hauptklasse für dein Plugin
class meinplugin(ScheduleMixin, SettingsMixin, UserInterfaceMixin, NavigationMixin, UrlsMixin, InvenTreePlugin):
    """meinplugin - Loan functionality plugin."""

    # Plugin metadata
    TITLE = "Leihsystem Plugin" # Angepasster Titel
    NAME = "LoanPlugin" # Slightly more descriptive internal name
    SLUG = "loan" # Changed slug to 'loan' - more meaningful! Update NAVIGATION link too!
    DESCRIPTION = "Plugin zum Verwalten von Leihvorgängen für Bestandsartikel"
    VERSION = PLUGIN_VERSION

    # Additional project information
    AUTHOR = "Jan Schüler"
    LICENSE = "MIT"

    # Optional: Gruppiere die Links unter einem eigenen Tab in der Navigation
    NAVIGATION_TAB_NAME = "Leihvorgänge"
    NAVIGATION_TAB_ICON = 'fas fa-handshake' # Example FontAwesome 4 Icon

    # Navigationselemente (von NavigationMixin)
    NAVIGATION = [
        {
            'name': _('Alle Leihvorgänge'), # Use translation
            'link': 'plugin:loan:loan_list', # URL-Name: plugin:<SLUG>:<url_name> -> SLUG is now 'loan'
            'icon': 'fas fa-list',
        },
        {
            'name': _('Neuer Leihvorgang'),
            'link': 'plugin:loan:loan_create', # Link to create view
            'icon': 'fas fa-plus-circle',
        },
    ]

    # URL-Definitionen (von UrlsMixin)
    # Use a separate urls.py for cleaner organization
    def setup_urls(self):
        """Definiert URL-Muster für dieses Plugin."""
        # Import late to prevent circular dependencies
        from . import urls as loan_urls
        return [
            # Delegate all plugin-specific URLs to meinplugin/urls.py
            path('', include((loan_urls, self.slug))),
        ]

    # --- Bestehende Mixin-Konfigurationen ---

    # Plugin settings (from SettingsMixin)
    SETTINGS = {
        'LOAN_LOCATION': {
            'name': _('Lagerort für Ausleihe'),
            'description': _('Wähle den Lagerort, an den Artikel während der Ausleihe verschoben werden'),
            'model': 'stock.stocklocation', # Link to StockLocation model
            'required': True, # Make this setting mandatory
        },
        # Example of existing setting:
        'CUSTOM_VALUE': {
             'name': 'Custom Value',
             'description': 'A custom value',
             'validator': int,
             'default': 42,
        }
        # Add more settings as needed (e.g., default loan duration, notification settings)
    }

    # ScheduleMixin placeholder
    SCHEDULED_TASKS = {}

    # UserInterfaceMixin placeholder (can be used later to add info to StockItem page)

    # --- Placeholder for Core Logic ---
    # These functions would handle the stock movement.
    # They would likely be called from the Views (e.g., form_valid).

    def issue_loan_item(self, loaned_item: 'LoanedItem', user: 'InvenTreeUser'):
         """Moves the StockItem to the designated loan location."""
         loan_location_pk = self.get_setting('LOAN_LOCATION')
         if not loan_location_pk:
             raise ValueError("Loan Location setting is not configured.")
         try:
             loan_location = StockLocation.objects.get(pk=loan_location_pk)
         except StockLocation.DoesNotExist:
             raise ValueError(f"Configured Loan Location (PK={loan_location_pk}) not found.")

         stock_item = loaned_item.stock_item

         # *** CORE LOGIC NEEDED HERE ***
         # Use InvenTree's internal API/functions to perform a stock transfer:
         # - Find the function like 'perform_stock_transfer' or similar.
         # - Parameters likely needed: stock_item, destination_location (loan_location),
         #   quantity (use stock_item.quantity), user performing action.
         # - Add notes to the transfer indicating it's for Loan #loaned_item.loan.pk.
         # - Handle potential errors (e.g., item not in expected location, insufficient permissions).
         print(f"Simulating: Transfer StockItem {stock_item.pk} to Location {loan_location.pk} for Loan {loaned_item.loan.pk}") # Placeholder

         # If transfer is successful:
         loaned_item.status = LoanedItem.ItemStatus.ON_LOAN
         loaned_item.save()
         # Optionally update Loan status if all items are now ON_LOAN

         return True # Indicate success


    def return_loan_item(self, loaned_item: 'LoanedItem', return_location: StockLocation, user: 'InvenTreeUser'):
         """Moves the StockItem back from the loan location to a specified return location."""
         loan_location_pk = self.get_setting('LOAN_LOCATION')
         if not loan_location_pk:
             raise ValueError("Loan Location setting is not configured.")
         try:
             loan_location = StockLocation.objects.get(pk=loan_location_pk)
         except StockLocation.DoesNotExist:
             raise ValueError(f"Configured Loan Location (PK={loan_location_pk}) not found.")

         stock_item = loaned_item.stock_item

         # Sanity check: Is the item actually at the loan location?
         if stock_item.location != loan_location:
             # Handle this error - maybe it was already returned or moved elsewhere?
             print(f"Warning: StockItem {stock_item.pk} is not at the expected Loan Location {loan_location.pk}.")
             # Decide how to proceed - maybe still mark as returned? Or raise error?
             # For now, we'll proceed cautiously and assume it needs marking returned.
             # In a real implementation, raise an error or provide user feedback.

         # *** CORE LOGIC NEEDED HERE ***
         # Use InvenTree's internal API/functions to perform a stock transfer:
         # - Find the function like 'perform_stock_transfer'.
         # - Parameters: stock_item, destination_location (return_location),
         #   quantity, user.
         # - Add notes indicating return from Loan #loaned_item.loan.pk.
         # - Handle potential errors.
         print(f"Simulating: Transfer StockItem {stock_item.pk} FROM Location {loan_location.pk} TO {return_location.pk} for Loan {loaned_item.loan.pk}") # Placeholder

         # If transfer is successful (or we decide to mark as returned anyway):
         loaned_item.status = LoanedItem.ItemStatus.RETURNED
         loaned_item.save()

         # Update the main Loan status if all items are returned
         loan = loaned_item.loan
         if all(item.status == LoanedItem.ItemStatus.RETURNED for item in loan.items.all()):
             from datetime import date
             loan.status = Loan.LoanStatus.RETURNED
             loan.return_date = date.today() # Set actual return date
             loan.save()

         return True # Indicate success
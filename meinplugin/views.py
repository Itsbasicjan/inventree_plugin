# meinplugin/views.py
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin # Ensure user is logged in
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden # For permission checks

# Import models from this plugin
from .models import Loan, LoanedItem

# Need StockLocation for return process (if not handled purely by actions)
from stock.models import StockLocation, StockItem

# Import the plugin class itself to access settings and methods
# Use InvenTree method to get plugin reference
from plugin import registry

class LoanPluginMixin(LoginRequiredMixin):
    """Mixin to share common logic for Loan views, like getting the plugin instance."""

    def get_plugin(self):
        # Get reference to our plugin instance (assuming slug is 'loan')
        # Requires plugin to be loaded and activated
        plugin = registry.get_plugin('loan')
        if not plugin:
            # This should not happen if the plugin is active, but handle defensively
            raise RuntimeError("Loan plugin (slug='loan') not found or not active.")
        return plugin

    # TODO: Add permission checks here if custom permissions are defined
    # def check_perms(self, request):
    #     if not request.user.has_perm('meinplugin.view_loan'): # Example permission
    #         raise PermissionDenied


class LoanListView(LoanPluginMixin, ListView):
    """View to list all Loans."""
    model = Loan
    template_name = 'meinplugin/loan_list.html' # Specify our template
    context_object_name = 'loans' # Name for the list in the template
    paginate_by = 25 # Optional pagination

    def get_queryset(self):
        # Order loans, newest first
        return Loan.objects.order_by('-loan_date')


class LoanDetailView(LoanPluginMixin, DetailView):
    """View to display details of a single Loan."""
    model = Loan
    template_name = 'meinplugin/loan_detail.html'
    context_object_name = 'loan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related items to the context
        context['loaned_items'] = self.object.items.all().select_related('stock_item')
        # Provide locations for the return form (simplified example)
        context['return_locations'] = StockLocation.objects.filter(structural=False)
        return context

    # --- Example: Handling Actions via POST requests ---
    # This is one way to handle actions like issuing or returning items
    def post(self, request, *args, **kwargs):
        self.object = self.get_object() # Get the Loan object
        plugin = self.get_plugin()
        action = request.POST.get('action')

        # --- Action: Issue Pending Item ---
        if action == 'issue_item':
            item_pk = request.POST.get('item_pk')
            if not item_pk:
                # Handle error: No item specified
                return redirect(self.object.get_absolute_url()) # Redirect back

            item_to_issue = get_object_or_404(LoanedItem, pk=item_pk, loan=self.object)

            # Check if item is actually pending
            if item_to_issue.status == LoanedItem.ItemStatus.PENDING:
                try:
                    # Call the plugin's logic to perform the transfer
                    plugin.issue_loan_item(item_to_issue, request.user)
                    # Add success message (using Django messages framework)
                except Exception as e:
                    # Handle errors (log, show error message to user)
                    print(f"Error issuing item {item_to_issue.pk}: {e}")
                    # Add error message
            else:
                # Handle error: Item not in pending state
                print(f"Cannot issue item {item_to_issue.pk}: Status is {item_to_issue.status}")
                # Add warning message

            return redirect(self.object.get_absolute_url())

        # --- Action: Return Item ---
        elif action == 'return_item':
            item_pk = request.POST.get('item_pk')
            return_loc_pk = request.POST.get('return_location')

            if not item_pk or not return_loc_pk:
                 # Handle error: Missing data
                 return redirect(self.object.get_absolute_url())

            item_to_return = get_object_or_404(LoanedItem, pk=item_pk, loan=self.object)
            return_location = get_object_or_404(StockLocation, pk=return_loc_pk)

            # Check if item is actually on loan
            if item_to_return.status == LoanedItem.ItemStatus.ON_LOAN:
                 try:
                     # Call the plugin's logic to perform the transfer back
                     plugin.return_loan_item(item_to_return, return_location, request.user)
                     # Add success message
                 except Exception as e:
                     # Handle errors
                     print(f"Error returning item {item_to_return.pk}: {e}")
                     # Add error message
            else:
                 # Handle error: Item not on loan
                 print(f"Cannot return item {item_to_return.pk}: Status is {item_to_return.status}")
                 # Add warning message

            return redirect(self.object.get_absolute_url())

        # --- Action: Add Item (More complex - needs StockItem selection) ---
        elif action == 'add_item':
            stock_item_pk = request.POST.get('stock_item_pk')
            if stock_item_pk:
                 stock_item = get_object_or_404(StockItem, pk=stock_item_pk, serialized=True) # Ensure serialized

                 # **Validation Needed Here:**
                 # 1. Is the stock_item available (correct location, not deleted, etc.)?
                 # 2. Is it already part of *this* or another *active* loan?
                 # 3. Does the user have permission to move this item?

                 # If validation passes:
                 try:
                     LoanedItem.objects.create(
                         loan=self.object,
                         stock_item=stock_item,
                         status=LoanedItem.ItemStatus.PENDING # Starts as pending
                     )
                     # Add success message
                 except Exception as e: # Catch potential integrity errors etc.
                     print(f"Error adding item {stock_item_pk} to loan {self.object.pk}: {e}")
                     # Add error message

                 return redirect(self.object.get_absolute_url())
            else:
                 # Handle error: No stock item provided
                 return redirect(self.object.get_absolute_url())


        # Default: If action is unknown or not POST, show the detail page normally
        return super().get(request, *args, **kwargs)


class LoanCreateView(LoanPluginMixin, CreateView):
    """View to create a new Loan."""
    model = Loan
    template_name = 'meinplugin/loan_form.html'
    fields = ['customer', 'due_date', 'reference', 'notes'] # Fields editable by user
    # success_url = reverse_lazy('plugin:loan:loan_list') # Redirect to list after creation

    def get_success_url(self):
        # Redirect to the detail view of the newly created loan
        return reverse_lazy('plugin:loan:loan_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # Automatically set the creator before saving
        form.instance.created_by = self.request.user
        # Loan starts as PENDING
        form.instance.status = Loan.LoanStatus.PENDING
        return super().form_valid(form)

    def get_form(self, form_class=None):
        """Limit customer choices to actual customers."""
        form = super().get_form(form_class)
        # Filter the customer dropdown to only show companies marked as 'is_customer'
        form.fields['customer'].queryset = Company.objects.filter(is_customer=True)
        return form
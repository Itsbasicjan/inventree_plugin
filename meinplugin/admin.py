# meinplugin/admin.py
from django.contrib import admin
from .models import Loan, LoanedItem

class LoanedItemInline(admin.TabularInline):
    """Allows editing LoanedItems directly within the Loan admin page."""
    model = LoanedItem
    extra = 1 # Show one empty slot for adding items
    # Define fields to show/edit in the inline form
    fields = ('stock_item', 'status')
    # Make stock_item read-only after creation? Maybe.
    # readonly_fields = ('stock_item',)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """Admin interface for the Loan model."""
    list_display = ('id', 'customer', 'loan_date', 'due_date', 'status', 'return_date')
    list_filter = ('status', 'customer', 'due_date')
    search_fields = ('id', 'customer__name', 'reference')
    readonly_fields = ('loan_date', 'updated_at', 'created_by') # Fields not editable in admin
    inlines = [LoanedItemInline] # Embed LoanedItem editing

    # Optional: Automatically set created_by user
    def save_model(self, request, obj, form, change):
        if not obj.pk: # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(LoanedItem)
class LoanedItemAdmin(admin.ModelAdmin):
    """Admin interface for the LoanedItem model (optional, mainly for debugging)."""
    list_display = ('id', 'loan', 'stock_item', 'status')
    list_filter = ('status', 'loan__customer')
    search_fields = ('stock_item__serial', 'loan__id', 'loan__customer__name')
    # Make fields read-only maybe?
    # readonly_fields = ('loan', 'stock_item')
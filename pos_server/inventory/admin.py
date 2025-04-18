from django.contrib import admin
from .models import InventoryTransaction

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'transaction_type', 'quantity_change', 'reference_id', 'user', 'created_at')
    search_fields = ('product__name', 'reference_id', 'user__username')
    list_filter = ('transaction_type', 'created_at', 'user')
    readonly_fields = ('created_at',)

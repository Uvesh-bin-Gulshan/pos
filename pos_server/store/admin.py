from django.contrib import admin
from .models import Store

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'currency', 'created_at')
    search_fields = ('name', 'phone', 'email', 'tax_id')
    readonly_fields = ('created_at', 'updated_at')

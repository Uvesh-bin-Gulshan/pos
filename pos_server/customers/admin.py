from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'store', 'loyalty_points', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ('store',)
    readonly_fields = ('created_at', 'updated_at')

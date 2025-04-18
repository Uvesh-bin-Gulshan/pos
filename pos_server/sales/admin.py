from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'customer_name', 'customer_contact', 'status',
        'payment_method', 'payment_status', 'total_amount', 'store', 'created_at'
    )
    search_fields = ('order_number', 'customer__first_name', 'customer__last_name', 'guest_customer_phone')
    list_filter = ('status', 'payment_method', 'payment_status', 'store')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order', 'product', 'quantity', 'unit_price',
        'tax_amount', 'discount_amount', 'total_price'
    )
    search_fields = ('order__order_number', 'product__name')
    list_filter = ('product',)


# from django.contrib import admin
# from .models import *

# # Register your models here.
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('order_number', 'get_customer', 'total_amount', 'status')
    
#     def get_customer(self, obj):
#         return obj.customer_name
#     get_customer.short_description = 'Customer'


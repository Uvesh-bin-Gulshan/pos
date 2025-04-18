from django.contrib import admin
from .models import ProductCategory, Product

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'barcode', 'category', 'price', 'stock_quantity', 'store', 'updated_at')
    search_fields = ('name', 'sku', 'barcode')
    list_filter = ('category', 'is_taxable', 'store')
    readonly_fields = ('created_at', 'updated_at')

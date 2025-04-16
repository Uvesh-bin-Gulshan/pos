# products/serializers.py
from rest_framework import serializers
from .models import Product, ProductCategory

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'parent']
        read_only_fields = ['id']

class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'barcode', 'sku',
            'category', 'category_id', 'price', 'cost_price',
            'tax_rate', 'is_taxable', 'stock_quantity',
            'low_stock_threshold', 'image', 'store', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'store']

class ProductBulkUpdateSerializer(serializers.Serializer):
    products = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )

class ProductSearchSerializer(serializers.Serializer):
    search = serializers.CharField(required=False)
    category = serializers.IntegerField(required=False)
    min_price = serializers.DecimalField(
        required=False, 
        max_digits=10, 
        decimal_places=2
    )
    max_price = serializers.DecimalField(
        required=False, 
        max_digits=10, 
        decimal_places=2
    )
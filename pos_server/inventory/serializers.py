from rest_framework import serializers
from .models import InventoryTransaction
from products.serializers import ProductSerializer

class InventoryTransactionSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'product', 'product_details', 'quantity_change',
            'transaction_type', 'reference_id', 'notes', 'user',
            'user_name', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']

class InventoryAdjustmentSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    adjustment = serializers.IntegerField()
    reason = serializers.CharField(required=False)

class StockLevelSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    current_stock = serializers.IntegerField()
    low_stock = serializers.BooleanField()
    product_name = serializers.CharField()
    product_sku = serializers.CharField()

class InventoryReportSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    product_id = serializers.IntegerField(required=False)
    transaction_type = serializers.CharField(required=False)
from rest_framework import serializers
from .models import Store

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'phone', 'email', 
                'tax_id', 'currency', 'created_at']
        read_only_fields = ['created_at']

class StoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['name', 'address', 'phone', 'email', 'tax_id', 'currency']

class StoreStatsSerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    active_users = serializers.IntegerField()
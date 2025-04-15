from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    total_spent = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2,
        read_only=True
    )
    order_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 
            'address', 'loyalty_points', 'notes', 'store',
            'total_spent', 'order_count', 'created_at'
        ]
        read_only_fields = ['store', 'created_at']

class CustomerLoyaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'loyalty_points']
    
    def update(self, instance, validated_data):
        points = validated_data.get('loyalty_points', instance.loyalty_points)
        instance.loyalty_points = max(0, points)  # Prevent negative points
        instance.save()
        return instance

class CustomerSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False)
    min_orders = serializers.IntegerField(required=False, min_value=0)
    min_loyalty = serializers.IntegerField(required=False, min_value=0)
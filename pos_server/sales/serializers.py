from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_details', 'quantity',
            'unit_price', 'tax_amount', 'discount_amount',
            'total_price', 'notes'
        ]
        extra_kwargs = {'product': {'write_only': True}}

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'guest_customer_name',
            'guest_customer_phone', 'customer_name', 'customer_phone',
            'user', 'store', 'status', 'subtotal', 'tax_amount',
            'discount_amount', 'total_amount', 'payment_method',
            'payment_status', 'notes', 'created_at', 'items'
        ]
        read_only_fields = [
            'order_number', 'user', 'store', 'subtotal',
            'tax_amount', 'total_amount', 'created_at'
        ]
    
    def get_customer_name(self, obj):
        return obj.customer_name
    
    def get_customer_phone(self, obj):
        return obj.customer_contact
    
    def validate(self, data):
        if not data.get('customer') and not data.get('guest_customer_phone'):
            raise serializers.ValidationError(
                "Either customer or guest phone must be provided"
            )
        return data
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        # Calculate order totals
        subtotal = 0
        for item_data in items_data:
            item = OrderItem.objects.create(order=order, **item_data)
            subtotal += item.total_price
        
        # Update order totals
        order.subtotal = subtotal
        order.tax_amount = subtotal * 0.1  # Example 10% tax
        order.total_amount = order.subtotal + order.tax_amount - order.discount_amount
        order.save()
        
        # Generate order number
        order.order_number = f"ORD-{order.id:06d}"
        order.save()
        
        return order

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'payment_status']

class OrderStatsSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_orders = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F
from django.utils import timezone
from .models import InventoryTransaction
from products.models import Product
from .serializers import (
    InventoryTransactionSerializer,
    InventoryAdjustmentSerializer,
    StockLevelSerializer,
    InventoryReportSerializer
)

class InventoryTransactionViewSet(viewsets.ModelViewSet):
    queryset = InventoryTransaction.objects.select_related('product', 'user')
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['transaction_type', 'product', 'created_at']

    def get_queryset(self):
        return self.queryset.filter(product__store=self.request.user.store)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_adjustment(self, request):
        serializer = InventoryAdjustmentSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        
        results = []
        for item in serializer.validated_data:
            try:
                product = Product.objects.get(
                    id=item['product_id'],
                    store=request.user.store
                )
                
                # Create transaction
                transaction = InventoryTransaction.objects.create(
                    product=product,
                    quantity_change=item['adjustment'],
                    transaction_type='adjustment',
                    notes=item.get('reason', 'Bulk adjustment'),
                    user=request.user
                )
                
                # Update product stock
                product.stock_quantity = F('stock_quantity') + item['adjustment']
                product.save()
                product.refresh_from_db()
                
                results.append({
                    'product_id': product.id,
                    'new_quantity': product.stock_quantity,
                    'transaction_id': transaction.id
                })
            except Product.DoesNotExist:
                results.append({
                    'product_id': item['product_id'],
                    'error': 'Product not found'
                })
        
        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        low_stock_items = Product.objects.filter(
            store=request.user.store,
            stock_quantity__lte=F('low_stock_threshold')
        ).annotate(
            low_stock=models.Case(
                models.When(
                    stock_quantity__lte=F('low_stock_threshold'),
                    then=models.Value(True)
                ),
                default=models.Value(False),
                output_field=models.BooleanField()
            )
        )
        
        serializer = StockLevelSerializer(low_stock_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        serializer = InventoryReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        queryset = self.get_queryset().filter(
            created_at__date__gte=data['start_date'],
            created_at__date__lte=data['end_date']
        )
        
        if product_id := data.get('product_id'):
            queryset = queryset.filter(product_id=product_id)
        
        if transaction_type := data.get('transaction_type'):
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # Group by product and transaction type
        report_data = queryset.values(
            'product__name',
            'transaction_type'
        ).annotate(
            total_quantity=Sum('quantity_change'),
            count=Count('id')
        ).order_by('product__name')
        
        return Response(report_data)
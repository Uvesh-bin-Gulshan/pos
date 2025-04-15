from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from .models import Order
from .serializers import (
    OrderSerializer,
    OrderStatusSerializer,
    OrderStatsSerializer
)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related(
        'customer', 'user', 'store'
    ).prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = self.queryset.filter(store=self.request.user.store)
        
        # Filter by status if provided
        if status := self.request.query_params.get('status'):
            queryset = queryset.filter(status=status)
            
        # Filter by payment status if provided
        if payment_status := self.request.query_params.get('payment_status'):
            queryset = queryset.filter(payment_status=payment_status)
            
        # Filter by date range if provided
        if date_from := self.request.query_params.get('date_from'):
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to := self.request.query_params.get('date_to'):
            queryset = queryset.filter(created_at__lte=date_to)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            store=self.request.user.store
        )

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusSerializer(
            order, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        orders = self.get_queryset().filter(created_at__date=today)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        days = int(request.query_params.get('days', 7))
        date_from = timezone.now().date() - timedelta(days=days)
        
        stats = Order.objects.filter(
            store=request.user.store,
            created_at__date__gte=date_from
        ).annotate(
            date=F('created_at__date')
        ).values('date').annotate(
            total_orders=Count('id'),
            total_sales=Sum('total_amount')
        ).order_by('date')
        
        # Calculate average order value
        for day in stats:
            day['avg_order_value'] = (
                day['total_sales'] / day['total_orders'] 
                if day['total_orders'] > 0 else 0
            )
        
        serializer = OrderStatsSerializer(stats, many=True)
        return Response(serializer.data)
from django.shortcuts import render

# Create your views here.
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from sales.models import Order
from products.models import Product
from zakat.models import ZakatCalculation
from .serializers import (
    SalesReportSerializer,
    FinancialReportSerializer,
    ZakatReportSerializer
)

class SalesReportView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SalesReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        queryset = Order.objects.filter(
            store=request.user.store,
            created_at__date__gte=data['start_date'],
            created_at__date__lte=data['end_date']
        )
        
        if data['group_by'] == 'day':
            results = queryset.annotate(
                date=F('created_at__date')
            ).values('date').annotate(
                total_sales=Sum('total_amount'),
                order_count=Count('id')
            ).order_by('date')
        
        elif data['group_by'] == 'product':
            results = queryset.values(
                'items__product__name'
            ).annotate(
                total_sales=Sum('items__total_price'),
                quantity_sold=Sum('items__quantity')
            ).order_by('-total_sales')
        
        # Add other grouping options...
        
        return Response(results)

class FinancialReportView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FinancialReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        report = {}
        
        # Sales Summary
        orders = Order.objects.filter(
            store=request.user.store,
            created_at__date__gte=data['start_date'],
            created_at__date__lte=data['end_date']
        )
        
        report['total_sales'] = orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        report['total_tax'] = orders.aggregate(
            total=Sum('tax_amount')
        )['total'] or 0
        
        # Inventory Value
        report['inventory_value'] = Product.objects.filter(
            store=request.user.store
        ).aggregate(
            total=Sum(F('cost_price') * F('stock_quantity'))
        )['total'] or 0
        
        return Response(report)

class ZakatReportView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ZakatReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        zakat_calc = ZakatCalculation.objects.filter(
            store=request.user.store,
            zakat_year=data['year']
        ).first()
        
        if not zakat_calc:
            return Response(
                {"detail": "No zakat calculation found for this year"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        report = {
            'year': zakat_calc.zakat_year,
            'zakatable_amount': zakat_calc.total_zakatable_assets,
            'zakat_amount': zakat_calc.zakat_amount,
            'is_paid': zakat_calc.is_paid
        }
        
        if data['include_breakdown']:
            report['assets'] = list(zakat_calc.assets.values())
            report['liabilities'] = list(zakat_calc.liabilities.values())
        
        return Response(report)
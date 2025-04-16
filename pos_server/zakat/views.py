from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import ZakatCalculation
from .serializers import (
    ZakatCalculationSerializer,
    NisabValueSerializer,
    ZakatPaymentSerializer
)
from datetime import date

class ZakatCalculationViewSet(viewsets.ModelViewSet):
    queryset = ZakatCalculation.objects.select_related('store')
    serializer_class = ZakatCalculationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(store=self.request.user.store)
    
    @action(detail=False, methods=['post'])
    def calculate_nisab(self, request):
        serializer = NisabValueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        if data['calculation_method'] == 'gold':
            # Nisab = 87.48g of gold
            nisab_value = data['gold_price_per_gram'] * 87.48
        else:
            # Nisab = 612.36g of silver
            nisab_value = data['silver_price_per_gram'] * 612.36
        
        return Response({
            'nisab_value': round(nisab_value, 2),
            'currency': data['currency'],
            'calculation_method': data['calculation_method']
        })
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        zakat_calc = self.get_object()
        serializer = ZakatPaymentSerializer(zakat_calc, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save(is_paid=True, payment_date=date.today())
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        zakat_calc = self.get_object()
        zakat_calc.calculate_totals()
        return Response(self.get_serializer(zakat_calc).data)
    
    @action(detail=False, methods=['get'])
    def years(self, request):
        years = ZakatCalculation.objects.filter(
            store=request.user.store
        ).values_list('zakat_year', flat=True).distinct()
        return Response(sorted(years, reverse=True))
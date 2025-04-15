from django.shortcuts import render


from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from .models import Customer
from .serializers import (
    CustomerSerializer, 
    CustomerLoyaltySerializer,
    CustomerSearchSerializer
)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.annotate(
        total_spent=Sum('order__total_amount'),
        order_count=Count('order')
    )
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone']

    def get_queryset(self):
        # Only show customers from the user's store
        return self.queryset.filter(store=self.request.user.store)

    def perform_create(self, serializer):
        # Automatically assign to user's store
        serializer.save(store=self.request.user.store)

    @action(detail=True, methods=['patch'])
    def loyalty(self, request, pk=None):
        customer = self.get_object()
        serializer = CustomerLoyaltySerializer(
            customer, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        serializer = CustomerSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        queryset = self.get_queryset()
        
        if query := serializer.validated_data.get('query'):
            queryset = queryset.filter(
                models.Q(first_name__icontains=query) |
                models.Q(last_name__icontains=query) |
                models.Q(phone__icontains=query)
            )
        
        if min_orders := serializer.validated_data.get('min_orders'):
            queryset = queryset.filter(order_count__gte=min_orders)
            
        if min_loyalty := serializer.validated_data.get('min_loyalty'):
            queryset = queryset.filter(loyalty_points__gte=min_loyalty)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
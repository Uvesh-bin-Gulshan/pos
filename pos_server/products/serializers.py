from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, ProductCategory
from .serializers import (ProductSerializer, ProductCategorySerializer,
                         ProductBulkUpdateSerializer, ProductSearchSerializer)

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for categories

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category', 'store')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'barcode', 'sku']
    filterset_fields = ['category', 'is_taxable']

    def get_queryset(self):
        # Only show products from the user's store
        return self.queryset.filter(store=self.request.user.store)

    def perform_create(self, serializer):
        # Automatically assign to user's store
        serializer.save(store=self.request.user.store)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        serializer = ProductBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Process bulk updates (prices, stock, etc.)
        updated = 0
        for item in serializer.validated_data['products']:
            Product.objects.filter(
                id=item['id'], 
                store=request.user.store
            ).update(**item['fields'])
            updated += 1
            
        return Response({"updated": updated})

    @action(detail=False, methods=['get'])
    def search(self, request):
        serializer = ProductSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        queryset = self.filter_queryset(self.get_queryset())
        
        if serializer.validated_data.get('search'):
            queryset = queryset.filter(
                name__icontains=serializer.validated_data['search']
            )
        
        if serializer.validated_data.get('category'):
            queryset = queryset.filter(
                category_id=serializer.validated_data['category']
            )
            
        if serializer.validated_data.get('min_price'):
            queryset = queryset.filter(
                price__gte=serializer.validated_data['min_price']
            )
            
        if serializer.validated_data.get('max_price'):
            queryset = queryset.filter(
                price__lte=serializer.validated_data['max_price']
            )
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
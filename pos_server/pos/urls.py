from django.urls import path
from .views import (
    ProductListAPI, ProductDetailAPI, CustomerListAPI, CustomerDetailAPI,
    OrderListAPI, CreateOrderAPI, SalesReportAPI
)

urlpatterns = [
    # Product URLs
    path('products/', ProductListAPI.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailAPI.as_view(), name='product-detail'),

    # Customer URLs
    path('customers/', CustomerListAPI.as_view(), name='customer-list'),
    path('customers/<int:pk>/', CustomerDetailAPI.as_view(), name='customer-detail'),

    # Order URLs
    path('orders/', OrderListAPI.as_view(), name='order-list'),
    path('orders/create/', CreateOrderAPI.as_view(), name='create-order'),

    # Sales Report
    path('sales-report/', SalesReportAPI.as_view(), name='sales-report'),
]

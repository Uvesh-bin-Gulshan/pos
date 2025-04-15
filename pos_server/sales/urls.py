from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('orders/today/', OrderViewSet.as_view({'get': 'today'})),
    path('orders/stats/', OrderViewSet.as_view({'get': 'stats'})),
    path('orders/<int:pk>/update-status/', 
         OrderViewSet.as_view({'patch': 'update_status'})),
] + router.urls
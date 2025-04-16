from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import InventoryTransactionViewSet

router = DefaultRouter()
router.register(r'inventory-transactions', InventoryTransactionViewSet, basename='inventorytransaction')

urlpatterns = [
    path('inventory/bulk-adjustment/', 
         InventoryTransactionViewSet.as_view({'post': 'bulk_adjustment'})),
    path('inventory/low-stock/', 
         InventoryTransactionViewSet.as_view({'get': 'low_stock'})),
    path('inventory/generate-report/', 
         InventoryTransactionViewSet.as_view({'post': 'generate_report'})),
] + router.urls
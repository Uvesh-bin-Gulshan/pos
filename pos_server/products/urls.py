from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductCategoryViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-categories', ProductCategoryViewSet, basename='productcategory')

urlpatterns = [
    path('products/search/', ProductViewSet.as_view({'get': 'search'})),
    path('products/bulk-update/', ProductViewSet.as_view({'post': 'bulk_update'})),
] + router.urls
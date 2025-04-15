from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')

urlpatterns = [
    path('customers/search/', CustomerViewSet.as_view({'get': 'search'})),
] + router.urls
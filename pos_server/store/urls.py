from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import StoreViewSet

router = DefaultRouter()
router.register(r'stores', StoreViewSet, basename='store')

urlpatterns = [
    path('stores/my-store/', StoreViewSet.as_view({'get': 'my_store'})),
] + router.urls
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ZakatCalculationViewSet

router = DefaultRouter()
router.register(r'zakat-calculations', ZakatCalculationViewSet, basename='zakatcalculation')

urlpatterns = [
    path('zakat/calculate-nisab/', 
         ZakatCalculationViewSet.as_view({'post': 'calculate_nisab'})),
    path('zakat-calculations/<int:pk>/mark-paid/', 
         ZakatCalculationViewSet.as_view({'post': 'mark_paid'})),
    path('zakat-calculations/<int:pk>/recalculate/', 
         ZakatCalculationViewSet.as_view({'post': 'recalculate'})),
    path('zakat-calculations/years/', 
         ZakatCalculationViewSet.as_view({'get': 'years'})),
] + router.urls
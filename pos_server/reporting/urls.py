from django.urls import path
from .views import SalesReportView, FinancialReportView, ZakatReportView

urlpatterns = [
    path('reports/sales/', SalesReportView.as_view(), name='sales-report'),
    path('reports/financial/', FinancialReportView.as_view(), name='financial-report'),
    path('reports/zakat/', ZakatReportView.as_view(), name='zakat-report'),
]
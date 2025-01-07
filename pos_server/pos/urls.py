from django.urls import path
from .views import ProductListAPI
app_name=['pos']
urlpatterns = [
    path('products/', ProductListAPI.as_view(), name='product_list'),
]

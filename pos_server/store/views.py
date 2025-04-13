from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Store
from .serializers import StoreSerializer, StoreCreateSerializer, StoreStatsSerializer
from products.models import Product
from users.models import User

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return StoreCreateSerializer
        return StoreSerializer

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        store = self.get_object()
        stats = {
            'total_products': Product.objects.filter(store=store).count(),
            'total_sales': sum(order.total_amount for order in store.order_set.all()),
            'active_users': User.objects.filter(store=store, is_active=True).count()
        }
        serializer = StoreStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_store(self, request):
        if not request.user.store:
            return Response({"detail": "User has no store assigned"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        serializer = StoreSerializer(request.user.store)
        return Response(serializer.data)
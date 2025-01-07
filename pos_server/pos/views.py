from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from django.shortcuts import get_object_or_404
from django.db.models import Sum
import datetime


class ProductListAPI(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateOrderAPI(APIView):
    def post(self, request):
        data = request.data
        customer_id = data.get('customer_id')
        items = data.get('items', [])

        # Retrieve customer and create order
        customer = get_object_or_404(Customer, id=customer_id)
        order = Order.objects.create(customer=customer, created_by=request.user, total_amount=0)

        total_amount = 0
        for item in items:
            product = get_object_or_404(Product, id=item['product_id'])
            quantity = item['quantity']
            price = product.price
            if product.stock < quantity:
                return Response({"error": f"Not enough stock for {product.name}"}, status=status.HTTP_400_BAD_REQUEST)
            # Create order item
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            total_amount += price * quantity
            product.stock -= quantity
            product.save()

        order.total_amount = total_amount
        order.save()
        return Response({"order_id": order.id, "total_amount": total_amount}, status=status.HTTP_201_CREATED)
class SalesReportAPI(APIView):
    def get(self, request):
        period = request.GET.get('period', 'daily')  # Accept 'daily', 'weekly', 'monthly'

        if period == 'daily':
            orders = Order.objects.filter(created_at__date=datetime.date.today())
        elif period == 'weekly':
            orders = Order.objects.filter(created_at__gte=datetime.date.today() - datetime.timedelta(days=7))
        elif period == 'monthly':
            orders = Order.objects.filter(created_at__month=datetime.date.today().month)

        total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        return Response({"period": period, "total_sales": total_sales})
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum
import datetime
from .models import Product, Customer, Order, OrderItem
from .serializers import ProductSerializer, CustomerSerializer, OrderSerializer, OrderItemSerializer

# Product Views
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

class ProductDetailAPI(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# Customer Views
class CustomerListAPI(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerDetailAPI(APIView):
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def put(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()
        return Response({"message": "Customer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# Order Views
class OrderListAPI(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class CreateOrderAPI(APIView):
    def post(self, request):
        data = request.data
        customer_id = data.get('customer_id')
        items = data.get('items', [])

        customer = get_object_or_404(Customer, id=customer_id)
        order = Order.objects.create(customer=customer, created_by=request.user, total_amount=0)

        total_amount = 0
        for item in items:
            product = get_object_or_404(Product, id=item['product_id'])
            quantity = item['quantity']
            price = product.price

            if product.stock < quantity:
                return Response({"error": f"Not enough stock for {product.name}"}, status=status.HTTP_400_BAD_REQUEST)

            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            total_amount += price * quantity
            product.stock -= quantity
            product.save()

        order.total_amount = total_amount
        order.save()
        return Response({"order_id": order.id, "total_amount": total_amount}, status=status.HTTP_201_CREATED)

# Sales Report View
class SalesReportAPI(APIView):
    def get(self, request):
        period = request.GET.get('period', 'daily')  

        if period == 'daily':
            orders = Order.objects.filter(created_at__date=datetime.date.today())
        elif period == 'weekly':
            orders = Order.objects.filter(created_at__gte=datetime.date.today() - datetime.timedelta(days=7))
        elif period == 'monthly':
            orders = Order.objects.filter(created_at__month=datetime.date.today().month)

        total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        return Response({"period": period, "total_sales": total_sales})


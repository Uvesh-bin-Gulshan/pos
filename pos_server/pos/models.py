from django.db import models
from django.contrib.auth.models import User
import barcode 
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from django.db import models
from django.contrib.auth.models import User
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File

# ✅ Product Model  //inventory
class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=12, unique=True)  # SKU should be 12 digits for EAN-13 barcode
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)  # Default stock to 0
    barcode = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.barcode:
            EAN = barcode.get_barcode_class("ean13")
            ean = EAN(f'{self.sku:0>12}', writer=ImageWriter())
            buffer = BytesIO()
            ean.write(buffer)
            self.barcode.save(f'{self.sku}.png', File(buffer), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
        
# ✅ Supplier Model //purchase
class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name




# ✅ Purchase Model  //purchase
class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="purchases")
    purchased_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase from {self.supplier.name} on {self.created_at.date()}"

# ✅ Purchase Item Model  //purchase
class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        """Automatically increase stock when a purchase is recorded."""
        self.product.stock += self.quantity
        self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

        #//sales
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# ✅ Order Model //sales
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

# ✅ OrderItem Model //sales
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        """Automatically reduce stock when an order is placed."""
        if self.pk is None:  # New order item
            self.product.stock -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)




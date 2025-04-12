from django.db import models
from django.forms import ValidationError
from django.core.validators import MinValueValidator



class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Credit Card'),
        ('mobile', 'Mobile Payment'),
        ('other', 'Other'),
    )
    order_number=models.CharField(max_length=20,unique=True)
    customer=models.ForeignKey('customer.Customer',on_delete=models.SET_NULL,null=True,blank=True)
    guest_customer_phone = models.CharField(max_length=20, blank=True)
    is_guest_converted = models.BooleanField(default=False)  # Track if guest was later registered 
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True) 
    store=models.ForeignKey('store.Store',on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    @property
    def customer_name(self):
        """Returns the customer name whether registered or guest"""
        if self.customer:
            return str(self.customer)
        return self.guest_customer_name or "Guest Customer"
    
    @property
    def customer_contact(self):
        """Returns the customer contact info whether registered or guest"""
        if self.customer:
            return self.customer.phone
        return self.guest_customer_phone
    
    def clean(self):
        super().clean()
        if not self.customer and not self.guest_customer_phone:
            raise ValidationError("Either a registered customer or guest phone number must be provided.")
    class Meta:
        indexes = [
        models.Index(fields=['guest_customer_phone']),
        # models.Index(fields=['customer', 'guest_customer_name']),
        ]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} for Order #{self.order.order_number}"
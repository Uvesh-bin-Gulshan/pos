from django.db import models
class ProductCategory(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField(blank=True)
    parent=models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_taxable = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
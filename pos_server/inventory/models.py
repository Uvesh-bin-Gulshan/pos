from django.db import models

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
    )
    
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity_change = models.IntegerField()  # Positive for addition, negative for deduction
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference_id = models.CharField(max_length=50, blank=True)  # Could be order ID or other reference
    notes = models.TextField(blank=True)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.product.name}"
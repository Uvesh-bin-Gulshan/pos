from django.db import models

# Create your models here.
from django.db import models
from django.db.models import Sum

class ZakatCalculation(models.Model):
    ASSET_TYPES = (
        ('cash', 'Cash'),
        ('inventory', 'Inventory'),
        ('receivables', 'Receivables'),
        ('investments', 'Investments'),
        ('other', 'Other Assets'),
    )
    
    LIABILITY_TYPES = (
        ('payables', 'Payables'),
        ('loans', 'Loans'),
        ('other', 'Other Liabilities'),
    )
    
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE)
    calculation_date = models.DateField(auto_now_add=True)
    zakat_year = models.PositiveIntegerField()
    total_zakatable_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    nisab_value = models.DecimalField(max_digits=15, decimal_places=2)
    zakat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2.5)
    zakat_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_totals(self):
        """Calculate and update zakat totals"""
        self.total_zakatable_assets = self.assets.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        self.total_liabilities = self.liabilities.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        net_assets = self.total_zakatable_assets - self.total_liabilities
        self.zakat_amount = (net_assets * self.zakat_percentage / 100) if net_assets >= self.nisab_value else 0
        self.save()
    
    def __str__(self):
        return f"Zakat {self.zakat_year} - {self.store.name}"

class ZakatAsset(models.Model):
    zakat_calculation = models.ForeignKey(ZakatCalculation, on_delete=models.CASCADE, related_name='assets')
    asset_type = models.CharField(max_length=20, choices=ZakatCalculation.ASSET_TYPES)
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_asset_type_display()}: {self.description}"

class ZakatLiability(models.Model):
    zakat_calculation = models.ForeignKey(ZakatCalculation, on_delete=models.CASCADE, related_name='liabilities')
    liability_type = models.CharField(max_length=20, choices=ZakatCalculation.LIABILITY_TYPES)
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_liability_type_display()}: {self.description}"
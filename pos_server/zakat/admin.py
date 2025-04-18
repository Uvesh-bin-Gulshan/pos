from django.contrib import admin
from .models import ZakatCalculation, ZakatAsset, ZakatLiability

class ZakatAssetInline(admin.TabularInline):
    model = ZakatAsset
    extra = 1

class ZakatLiabilityInline(admin.TabularInline):
    model = ZakatLiability
    extra = 1

@admin.register(ZakatCalculation)
class ZakatCalculationAdmin(admin.ModelAdmin):
    list_display = (
        'store', 'zakat_year', 'calculation_date', 'total_zakatable_assets',
        'total_liabilities', 'zakat_amount', 'is_paid', 'payment_date'
    )
    list_filter = ('store', 'zakat_year', 'is_paid')
    search_fields = ('store__name',)
    readonly_fields = ('calculation_date', 'created_at', 'updated_at', 'zakat_amount', 'total_zakatable_assets', 'total_liabilities')
    inlines = [ZakatAssetInline, ZakatLiabilityInline]

@admin.register(ZakatAsset)
class ZakatAssetAdmin(admin.ModelAdmin):
    list_display = ('zakat_calculation', 'asset_type', 'description', 'amount', 'created_at')
    list_filter = ('asset_type',)
    search_fields = ('description',)

@admin.register(ZakatLiability)
class ZakatLiabilityAdmin(admin.ModelAdmin):
    list_display = ('zakat_calculation', 'liability_type', 'description', 'amount', 'created_at')
    list_filter = ('liability_type',)
    search_fields = ('description',)

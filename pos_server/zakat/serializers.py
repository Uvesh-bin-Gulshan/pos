from rest_framework import serializers
from .models import ZakatCalculation, ZakatAsset, ZakatLiability

class ZakatAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZakatAsset
        fields = ['id', 'asset_type', 'description', 'amount', 'created_at']
        read_only_fields = ['zakat_calculation', 'created_at']

class ZakatLiabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ZakatLiability
        fields = ['id', 'liability_type', 'description', 'amount', 'created_at']
        read_only_fields = ['zakat_calculation', 'created_at']

class ZakatCalculationSerializer(serializers.ModelSerializer):
    assets = ZakatAssetSerializer(many=True, required=False)
    liabilities = ZakatLiabilitySerializer(many=True, required=False)
    store_name = serializers.CharField(source='store.name', read_only=True)
    is_above_nisab = serializers.SerializerMethodField()
    
    class Meta:
        model = ZakatCalculation
        fields = [
            'id', 'store', 'store_name', 'calculation_date', 'zakat_year',
            'total_zakatable_assets', 'total_liabilities', 'nisab_value',
            'zakat_percentage', 'zakat_amount', 'is_paid', 'payment_date',
            'notes', 'is_above_nisab', 'assets', 'liabilities', 'created_at'
        ]
        read_only_fields = [
            'total_zakatable_assets', 'total_liabilities', 'zakat_amount',
            'created_at'
        ]
    
    def get_is_above_nisab(self, obj):
        return obj.total_zakatable_assets >= obj.nisab_value
    
    def create(self, validated_data):
        assets_data = validated_data.pop('assets', [])
        liabilities_data = validated_data.pop('liabilities', [])
        
        zakat_calc = ZakatCalculation.objects.create(**validated_data)
        
        # Create assets
        for asset_data in assets_data:
            ZakatAsset.objects.create(zakat_calculation=zakat_calc, **asset_data)
        
        # Create liabilities
        for liability_data in liabilities_data:
            ZakatLiability.objects.create(zakat_calculation=zakat_calc, **liability_data)
        
        # Calculate totals
        zakat_calc.calculate_totals()
        
        return zakat_calc

class NisabValueSerializer(serializers.Serializer):
    gold_price_per_gram = serializers.DecimalField(max_digits=10, decimal_places=2)
    silver_price_per_gram = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3)
    calculation_method = serializers.ChoiceField(choices=['gold', 'silver'])

class ZakatPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZakatCalculation
        fields = ['is_paid', 'payment_date', 'notes']
        extra_kwargs = {
            'payment_date': {'required': True},
            'notes': {'required': False}
        }
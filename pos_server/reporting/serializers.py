from rest_framework import serializers

class SalesReportSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    group_by = serializers.ChoiceField(
        choices=['day', 'week', 'month', 'product', 'category']
    )

class FinancialReportSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    report_type = serializers.ChoiceField(
        choices=['summary', 'detailed', 'tax']
    )

class ZakatReportSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    include_breakdown = serializers.BooleanField(default=False)
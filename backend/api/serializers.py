from rest_framework import serializers


class TaxtCalculationRequestSerializer(serializers.Serializer):
    tax_type = serializers.ChoiceField(choices = ['IVA', 'ISR'])
    amount = serializers.DecimalField(max_digits = 14, decimal_places = 2)
    applies_to = serializers.CharField(required = False, default = 'general')
    as_of_date = serializers.DateField(required = False)



class TaxCalculationResponseSerializer(serializers.Serializer):
    tax_type = serializers.CharField()
    input_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    rule_set_id = serializers.UUIDField()
    rule_set_effective_date = serializers.DateField()


class TaxRuleSerializer(serializers.Serializer):
    rule_type = serializers.ChoiceField(choices=['IVA', 'ISR', 'RETENCION'])
    applies_to = serializers.CharField(default='general')
    rate = serializers.DecimalField(max_digits=6, decimal_places=4, required=False, allow_null=True)
    formula_expression = serializers.JSONField(required=False, allow_null=True)


class TaxRuleSetCreateSerializer(serializers.Serializer):
    jurisdiction = serializers.CharField(default='MX')
    effective_date = serializers.DateField()
    published_gazette_ref = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    rules = TaxRuleSerializer(many=True)


class TaxRuleSetSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    jurisdiction = serializers.CharField()
    effective_date = serializers.DateField()
    status = serializers.CharField()
    published_gazette_ref = serializers.CharField()
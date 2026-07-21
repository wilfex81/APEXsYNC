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
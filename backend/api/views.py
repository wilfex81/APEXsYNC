from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tax_engine.services import get_active_rule_set
from tax_engine.calculator import calculate_iva, calculate_isr
from .serializers import TaxtCalculationRequestSerializer

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TaxCalculateView(APIView):
    def post(self, request):
        req = TaxtCalculationRequestSerializer(data = request.data)
        req.is_valid(raise_exception = True)
        data = req.validated_data


        rule_set = get_active_rule_set(as_of = data.get('as_of_date'))
        if not rule_set:
            return Response(
                {"error": "No active tax rule set found for the given data."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        rule = rule_set.rules.filter(
            rule_type = data['tax_type'], applies_to = data['applies_to']
        ).first()
        if not rule:
            return Response(
                {"error": f"No {data['tax_type']} rule found for '{data['applies_to']}' in active rule set."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if data['tax_type'] == 'IVA':
            tax_amount = calculate_iva(data['amount'], rule)
        else:
            tax_amount = calculate_isr(data['amount'], rule)

        return Response({
            "tax_type": data['tax_type'],
            "input_amount": data['amount'],
            "tax_amount": tax_amount,
            "rule_set_id": rule_set.id,
            "rule_set_effective_date": rule_set.effective_date
        })
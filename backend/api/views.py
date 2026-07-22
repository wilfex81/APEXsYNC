from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tax_engine.models import TaxRule, TaxRuleSet
from tax_engine.services import get_active_rule_set, publish_rule_set
from tax_engine.calculator import calculate_iva, calculate_isr
from .serializers import (
    TaxRuleSetSerializer, TaxtCalculationRequestSerializer,
    TaxRuleSetCreateSerializer, TaxCalculationResponseSerializer,
    TaxRuleSerializer
    )

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
    
class TaxRuleSetListCreateView(APIView):
    def get(self, request):
        rule_sets = TaxRuleSet.objects.all()
        data = TaxRuleSetSerializer(rule_sets, many=True).data
        return Response(data)
    
    def post(self, request):
        req = TaxRuleSetCreateSerializer(data = request.data)
        req.is_valid(raise_exception=True)
        payload = req.validated_data
        rules_data = payload.pop('rules')

        rule_set = TaxRuleSet.objects.create(status = 'draft', **payload)
        for rule_data in rules_data:
            TaxRule.objects.create(rule_set = rule_set, **rule_data)

        return Response(
            TaxRuleSetSerializer(rule_set).data,
            status=status.HTTP_201_CREATED
        )
    

class TaxRuleSetPublishView(APIView):
    def post(self, request, rule_set_id):
        try:
            rule_set = TaxRuleSet.objects.get(id = rule_set_id)
        except TaxRuleSet.DoesNotExist:
            return Response({"error": "Rule set not found."}, status=status.HTTP_404_NOT_FOUND)
        

        if rule_set.status == 'active':
            return Response({"error": "Rule set is already active."}, status=status.HTTP_400_BAD_REQUEST)
        
        published_by = request.data.get('published_by', 'api_user')
        publish_rule_set(rule_set, published_by=published_by)

        return Response(TaxRuleSetSerializer(rule_set).data)
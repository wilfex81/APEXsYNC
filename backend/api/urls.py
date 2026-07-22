from django.urls import path
from .views import (
    TaxCalculateView, TaxRuleSetListCreateView, 
    TaxRuleSetPublishView
)

urlpatterns = [
    path('tax/calculate/', TaxCalculateView.as_view(), name='tax-calculate'),
    path('tax/rule-sets/', TaxRuleSetListCreateView.as_view(), name='tax-rule-sets'),
    path('tax/rule-sets/<uuid:rule_set_id>/publish/', TaxRuleSetPublishView.as_view(), name='tax-rule-set-publish'),
]
from django.urls import path
from .views import (
    TaxCalculateView, TaxRuleSetListCreateView, 
    TaxRuleSetPublishView, ForecastView,
    AnomalyView
)

urlpatterns = [
    path('tax/calculate/', TaxCalculateView.as_view(), name='tax-calculate'),
    path('tax/rule-sets/', TaxRuleSetListCreateView.as_view(), name='tax-rule-sets'),
    path('tax/rule-sets/<uuid:rule_set_id>/publish/', TaxRuleSetPublishView.as_view(), name='tax-rule-set-publish'),
    path('analytics/forecast/', ForecastView.as_view(), name='analytics-forecast'),
    path('analytics/anomalies/', AnomalyView.as_view(), name='analytics-anomalies'),
]
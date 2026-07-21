from datetime import date
from .models import TaxRuleSet


def get_active_rule_set(jurisdiction = 'MX', as_of: date = None):
    as_of = as_of or date.today()
    return TaxRuleSet.objects.filter(
        jurisdiction = jurisdiction,
        status = 'active',
        effective_date__lte = as_of,
    ).order_by('-effective_date').first()

def publish_rule_set(rule_set: TaxRuleSet, published_by: str):
    """Atomically activate a draft rule set and supersede the previou active one."""
    from django.db import transaction
    from django.utils import timezone

    with transaction.atomic():
        TaxRuleSet.objects.filter(
            jurisdiction = rule_set.jurisdiction, status = 'active'
        ).update(status = 'superseded')

        rule_set.status = 'active'
        rule_set.published_by = published_by
        rule_set.published_at = timezone.now()
        rule_set.save()

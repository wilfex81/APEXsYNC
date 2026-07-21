from django.core.management.base import BaseCommand
from decimal import Decimal
from tax_engine.models import TaxRuleSet, TaxRule
from tax_engine.services import publish_rule_set

ISR_MONTHLY_BRACKETS_2026 = [
    {"min": 0.01, "max": 844.59, "fixed_fee": 0.00, "rate": 0.0192},
    {"min": 844.60, "max": 7168.51, "fixed_fee": 16.22, "rate": 0.0640},
    {"min": 7168.52, "max": 12598.02, "fixed_fee": 420.95, "rate": 0.1088},
    {"min": 12598.03, "max": 14644.64, "fixed_fee": 1011.68, "rate": 0.1600},
    {"min": 14644.65, "max": 17533.64, "fixed_fee": 1339.14, "rate": 0.1792},
    {"min": 17533.65, "max": 35362.83, "fixed_fee": 1856.84, "rate": 0.2136},
    {"min": 35362.84, "max": 55736.68, "fixed_fee": 5665.16, "rate": 0.2352},
    {"min": 55736.69, "max": 106410.50, "fixed_fee": 10457.09, "rate": 0.3000},
    {"min": 106410.51, "max": 141880.66, "fixed_fee": 25659.23, "rate": 0.3200},
    {"min": 141880.67, "max": 425641.99, "fixed_fee": 37009.69, "rate": 0.3400},
    {"min": 425642.00, "max": None, "fixed_fee": 133488.54, "rate": 0.3500},
]


class Command(BaseCommand):
    help = "Seeds the 2026 IVA + ISR (monthly, personas físicas) rule set"

    def handle(self, *args, **options):
        rule_set = TaxRuleSet.objects.create(
            jurisdiction='MX',
            effective_date='2026-01-01',
            published_gazette_ref='DOF - Anexo 8 RMF 2026 (publicado 28-dic-2025)',
            status='draft',
            notes='ISR mensual personas físicas + IVA general. Fuente: Anexo 8, RMF 2026.',
        )

        # IVA — flat rate, no brackets needed
        TaxRule.objects.create(
            rule_set=rule_set,
            rule_type='IVA',
            applies_to='general',
            rate=Decimal('0.16'),
        )

        # ISR — bracket-based, monthly, personas físicas (Art. 96 LISR)
        TaxRule.objects.create(
            rule_set=rule_set,
            rule_type='ISR',
            applies_to='personas_fisicas_mensual',
            formula_expression={"brackets": ISR_MONTHLY_BRACKETS_2026},
        )

        publish_rule_set(rule_set, published_by='seed_command')
        self.stdout.write(self.style.SUCCESS(
            f"Seeded and activated rule set {rule_set.id} effective {rule_set.effective_date}"
        ))
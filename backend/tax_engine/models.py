from django.db import models
import uuid

class TaxRuleSet(models.Model):
    """A versioned bundle of tax rules, published from a Gaceta official update."""
    STATUS_CHOICES = [
        ('draft', 'Darft'),
        ('active', 'Active'),
        ('superseded', 'Superseded')
    ]

    id = models.UUIDField(primary_key = True, default=uuid.uuid4, editable=False)
    jurisdiction = models.CharField(max_length=50, default='MX')
    effective_date = models.DateField(help_text="Date this rule set takes effect")
    published_gazette_ref = models.CharField(
        max_length=255, blank=True,
        help_text="Refernce to the Gaceta official / DOF publication"
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    published_by = models.CharField(max_length=255, blank = True, help_text="Whi approved this rule set")
    published_at = models.DateTimeField(null = True, blank = True)

    class Meta:
        indexes = [
            models.Index(fields=['jurisdiction', 'status', 'effective_date'])
        ]

        ordering = ['effective_date']

class TaxRule(models.Model):
    """A single rule within a rule set - e.g. one IVA rate, or one ISR bracket."""
    RULE_TYPE_CHOICES = [
        ('IVA', 'IVA / VAT'),
        ('ISR', 'ISR / Income Tax'),
        ('RETENCION', 'Retencion')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_set = models.ForeignKey(TaxRuleSet, on_delete=models.CASCADE, related_name='rules')
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    applies_to = models.CharField(
        max_length=100, blank=True,
        help_text="Category, income bracket label, or entity type this rule applies to"
    )
    rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    min_threshold = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    max_threshold = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fixed_fee = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, default=0)
    formula_expression = models.JSONField(
        null=True, blank=True,
        help_text="Optional structured expression for non-trivial calculations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rule_type} {self.rate} [{self.min_threshold}-{self.max_threshold}]"
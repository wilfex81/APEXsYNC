from django.db import models
import uuid


class Entity(models.Model):
    """A business/taxpayer entity — the root of everything."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rfc = models.CharField(max_length=13, unique=True, help_text="Mexican tax ID")
    name = models.CharField(max_length=255)
    entity_type = models.CharField(
        max_length=20,
        choices=[('persona_fisica', 'Persona Física'), ('persona_moral', 'Persona Moral')]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.rfc})"


class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='accounts')
    account_type = models.CharField(
        max_length=20,
        choices=[('checking', 'Checking'), ('savings', 'Savings'), ('credit', 'Credit')]
    )
    currency = models.CharField(max_length=3, default='MXN')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entity.name} - {self.account_type}"


class Category(models.Model):
    """Expense/income categories — used by both normalization and analytics."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')

    def __str__(self):
        return self.name


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.CharField(max_length=500, blank=True)
    source_doc_ref = models.CharField(max_length=255, blank=True, help_text="Reference to source document/invoice")
    is_duplicate_flag = models.BooleanField(default=False)
    confidence_score = models.FloatField(null=True, blank=True, help_text="Confidence in dedup/anomaly flagging")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['account', 'date']),
        ]

    def __str__(self):
        return f"{self.date} | {self.amount} | {self.description[:30]}"


class InventorySnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='inventory_snapshots')
    sku = models.CharField(max_length=100)
    date = models.DateField()
    qty = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    turnover_rate = models.FloatField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['entity', 'sku', 'date']),
        ]

    def __str__(self):
        return f"{self.sku} @ {self.date}"


class CashFlowEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='cash_flow_events')
    date = models.DateField()
    event_type = models.CharField(
        max_length=20,
        choices=[('inflow', 'Inflow'), ('outflow', 'Outflow')]
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    projected = models.BooleanField(default=False, help_text="True if forecasted, False if actual")

    class Meta:
        indexes = [
            models.Index(fields=['entity', 'date']),
        ]

    def __str__(self):
        return f"{self.event_type} {self.amount} on {self.date}"
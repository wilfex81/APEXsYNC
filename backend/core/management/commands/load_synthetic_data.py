import json
from pathlib import Path
from django.core.management.base import BaseCommand
from core.models import (
    Entity, Account, 
    Category, Transaction, 
    InventorySnapshot, CashFlowEvent
)

RAW_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "data_pipeline" / "synthetic_data" / "raw_feed"


class Command(BaseCommand):
    help = "Loads the synthetic raw feed into core Django models (pre-dbt bridge)"

    def handle(self, *args, **options):
        transactions = json.loads((RAW_DIR / "transactions.json").read_text())
        cashflow = json.loads((RAW_DIR / "cashflow.json").read_text())
        inventory = json.loads((RAW_DIR / "inventory.json").read_text())

        entity_rfc = transactions[0]["rfc_receptor"]
        entity, _ = Entity.objects.get_or_create(
            rfc=entity_rfc,
            defaults={"name": "Synthetic Test Entity SA de CV", "entity_type": "persona_moral"},
        )
        account, _ = Account.objects.get_or_create(
            entity=entity, account_type="checking", defaults={"currency": "MXN"}
        )

        cat_cache = {}
        for record in transactions:
            cat_name = record["conceptos"][0]["categoria"]
            if cat_name not in cat_cache:
                cat_cache[cat_name], _ = Category.objects.get_or_create(name=cat_name)

            Transaction.objects.create(
                account=account,
                category=cat_cache[cat_name],
                date=record["fecha_emision"],
                amount=record["total"],
                description=record["conceptos"][0]["descripcion"],
                source_doc_ref=record["uuid"],
            )

        for record in cashflow:
            CashFlowEvent.objects.create(
                entity=entity,
                date=record["date"],
                event_type=record["type"],
                amount=record["amount"],
                projected=False,
            )

        for record in inventory:
            InventorySnapshot.objects.create(
                entity=entity,
                sku=record["sku"],
                date=record["date"],
                qty=record["qty"],
                unit_cost=record["unit_cost"],
                turnover_rate=record["turnover_rate"],
            )

        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(transactions)} transactions, {len(cashflow)} cash flow events, "
            f"{len(inventory)} inventory snapshots for entity {entity_rfc}"
        ))
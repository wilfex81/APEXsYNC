"""
Synthetic CFDI/CFE-style financial record generator.

IMPORTANT: All values are fabricated. Field structure mimics real Mexican
fiscal document conventions (CFDI 4.0 fields: RFC, UUID, Folio, Conceptos)
for realism, but no real entities, RFCs, or transactions are represented.
"""
import json
import uuid
import random
from datetime import date, timedelta
from pathlib import Path
from faker import Faker
import numpy as np

fake = Faker('es_MX')
random.seed(42)
np.random.seed(42)

OUTPUT_DIR = Path(__file__).parent / "raw_feed"
OUTPUT_DIR.mkdir(exist_ok=True)

CATEGORIES = [
    "materia_prima", "renta", "nomina", "servicios_publicos",
    "mantenimiento", "logistica", "marketing", "insumos_oficina",
]

SKUS = [f"SKU-{i:04d}" for i in range(1, 41)]


def fake_rfc(is_moral=False):
    if is_moral:
        return fake.bothify(text='???######???').upper()
    return fake.bothify(text='????######???').upper()


def generate_cfdi_record(entity_rfc: str, txn_date: date, base_amount: float, category: str):
    """One synthetic CFDI-style invoice record."""
    subtotal = round(base_amount, 2)
    iva = round(subtotal * 0.16, 2)
    total = round(subtotal + iva, 2)
    return {
        "uuid": str(uuid.uuid4()),
        "folio": fake.bothify(text='F-#####'),
        "fecha_emision": txn_date.isoformat(),
        "rfc_emisor": fake_rfc(is_moral=True),
        "rfc_receptor": entity_rfc,
        "conceptos": [{
            "descripcion": fake.bs(),
            "categoria": category,
            "cantidad": 1,
            "valor_unitario": subtotal,
        }],
        "subtotal": subtotal,
        "iva": iva,
        "total": total,
        "moneda": "MXN",
        "metodo_pago": random.choice(["PUE", "PPD"]),
        "forma_pago": random.choice(["01", "03", "04"]),  # efectivo, transferencia, tarjeta
    }


def generate_cashflow_series(entity_rfc: str, start: date, months: int = 24):
    """
    Generates a monthly cash flow time series with trend + seasonality + noise,
    so the forecasting model in Phase 4 has something real to fit against.
    """
    records = []
    base = 150_000
    trend = np.linspace(0, 40_000, months)  # gradual growth
    seasonality = 20_000 * np.sin(np.linspace(0, 4 * np.pi, months))  # yearly-ish cycle
    noise = np.random.normal(0, 8_000, months)

    for i in range(months):
        month_date = start + timedelta(days=30 * i)
        inflow = max(base + trend[i] + seasonality[i] + noise[i], 10_000)
        outflow = inflow * random.uniform(0.65, 0.85)
        records.append({
            "entity_rfc": entity_rfc,
            "date": month_date.replace(day=1).isoformat(),
            "type": "inflow",
            "amount": round(inflow, 2),
        })
        records.append({
            "entity_rfc": entity_rfc,
            "date": month_date.replace(day=1).isoformat(),
            "type": "outflow",
            "amount": round(outflow, 2),
        })
    return records


def generate_inventory_series(entity_rfc: str, start: date, months: int = 24):
    records = []
    for sku in SKUS:
        base_qty = random.randint(50, 500)
        unit_cost = round(random.uniform(20, 800), 2)
        # a handful of SKUs simulate slow-moving "muda" — flat/declining turnover
        is_slow_mover = random.random() < 0.15
        for i in range(months):
            month_date = (start + timedelta(days=30 * i)).replace(day=1)
            if is_slow_mover:
                qty = max(base_qty - i * random.randint(0, 2), base_qty * 0.6)
                turnover = round(random.uniform(0.05, 0.3), 3)
            else:
                qty = base_qty + np.random.normal(0, 15)
                turnover = round(random.uniform(0.8, 2.5), 3)
            records.append({
                "entity_rfc": entity_rfc,
                "sku": sku,
                "date": month_date.isoformat(),
                "qty": max(int(qty), 0),
                "unit_cost": unit_cost,
                "turnover_rate": turnover,
            })
    return records


def generate_transaction_batch(entity_rfc: str, start: date, months: int = 24, inject_duplicates=True):
    """Expense/income invoice records, with a controlled % of injected duplicates
    for the normalization module (Phase 5) to detect."""
    records = []
    for i in range(months):
        month_date = (start + timedelta(days=30 * i)).replace(day=1)
        n_txns = random.randint(15, 30)
        for _ in range(n_txns):
            category = random.choice(CATEGORIES)
            amount = round(random.uniform(500, 25_000), 2)
            txn_date = month_date + timedelta(days=random.randint(0, 27))
            record = generate_cfdi_record(entity_rfc, txn_date, amount, category)
            records.append(record)

            if inject_duplicates and random.random() < 0.04:
                dup = dict(record)
                dup["uuid"] = str(uuid.uuid4())  # different UUID, same amount/date/vendor — realistic dup pattern
                dup["folio"] = fake.bothify(text='F-#####')
                records.append(dup)
    return records


def main():
    entity_rfc = fake_rfc(is_moral=True)
    start = date(2024, 1, 1)

    transactions = generate_transaction_batch(entity_rfc, start)
    cashflow = generate_cashflow_series(entity_rfc, start)
    inventory = generate_inventory_series(entity_rfc, start)

    (OUTPUT_DIR / "transactions.json").write_text(json.dumps(transactions, indent=2, ensure_ascii=False))
    (OUTPUT_DIR / "cashflow.json").write_text(json.dumps(cashflow, indent=2, ensure_ascii=False))
    (OUTPUT_DIR / "inventory.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False))

    print(f"Generated synthetic feed for entity {entity_rfc}")
    print(f"  {len(transactions)} transaction records (~{sum(1 for _ in transactions)} incl. injected dupes)")
    print(f"  {len(cashflow)} cash flow records")
    print(f"  {len(inventory)} inventory snapshot records")
    print(f"  Written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
from django.db import connection
import pandas as pd


def get_monthly_cashflow(entity_id) -> pd.DataFrame:
    query = """
        SELECT month, total_flow AS total_inflow, total_outflow, net_cashflow
        FROM dbt_apexsync.mart_monthly_cashflow
        WHERE entity_id = %s
        ORDER BY month
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [str(entity_id)])
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


def get_inventory_turnover(entity_id) -> pd.DataFrame:
    query = """
        SELECT sku, month, avg_qty, avg_turnover_rate, inventory_value
        FROM dbt_apexsync.mart_inventory_turnover
        WHERE entity_id = %s
        ORDER BY sku, month
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [str(entity_id)])
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)

def get_duplicate_transactions(account_id=None) -> list:
    query = """
        SELECT transaction_id, account_id, transaction_date, amount, description,
               dup_group_size, dup_rank
        FROM dbt_apexsync.stg_transactions_deduped
        WHERE is_likely_duplicate = true
    """
    params = []
    if account_id:
        query += " AND account_id = %s"
        params.append(str(account_id))
    query += " ORDER BY transaction_date, amount"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_cost_spike_flags(account_id=None) -> list:
    query = """
        SELECT account_id, category, month, total_amount, rolling_6mo_avg,
               pct_above_rolling_avg, flag_reason
        FROM dbt_apexsync.mart_profitability_flags
    """
    params = []
    if account_id:
        query += " WHERE account_id = %s"
        params.append(str(account_id))
    query += " ORDER BY month DESC"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
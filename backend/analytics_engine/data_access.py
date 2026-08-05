from django.db import connection
import pandas as pd


def get_monthly_cashflow(entity_id) -> pd.DataFrame:
    query = """
        SELECT month, total_inflow, total_outflow, net_cashflow
        FROM dbt_apexsync.mart_monthly_cashflow
        WHERE entity_id = %s
        ORDER BY month
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [str(entity_id)])
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


def get_inventory_turonver(entity_id) -> pd.DataFrame:
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
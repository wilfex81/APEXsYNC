with inventory as (
    select * from {{ ref('stg_inventory') }}
)

select
    entity_id,
    sku,
    date_trunc('month', snapshot_date)::date as month,
    avg(quantity) as avg_qty,
    avg(turnover_rate) as avg_turnover_rate,
    avg(unit_cost) * avg(quantity) as inventory_value
from inventory
group by 1, 2, 3
order by 1, 2, 3
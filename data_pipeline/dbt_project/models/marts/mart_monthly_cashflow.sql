with cashflow as (
    select * from {{ ref('stg_cashflow') }}
)

select 
    entity_id,
    date_trunc('month', event_date):: date as month,
    sum(case when event_type = 'inflow' then amount else 0 end) as total_flow,
    sum(case when event_type = 'outflow' then amount else 0 end) as total_outflow,
    sum(case when event_type = 'inflow' then amount else -amount end) as net_cashflow
from cashflow
where not projected
group by 1, 2
order by 1, 2

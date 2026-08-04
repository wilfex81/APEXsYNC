with txns as (
    select * from {{ ref('stg_transactions_deduped') }}
),

categories as (
    select * from {{ source('core', 'core_category') }}
)

select
    t.account_id,
    date_trunc('month', t.transaction_date)::date as month,
    c.name as category,
    count(*) filter (where not t.is_duplicate_secondary) as transaction_count,
    sum(t.amount) filter (where not t.is_duplicate_secondary) as total_amount,
    count(*) filter (where t.is_likely_duplicate) as flagged_duplicate_count
from txns t
left join categories c on t.category_id = c.id
group by 1, 2, 3
order by 1, 2
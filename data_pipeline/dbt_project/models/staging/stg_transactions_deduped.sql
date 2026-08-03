with base as (
    select * from {{ ref('stg_transactions') }}
),

flagged as (
    select 
        *,
        count(*) over (
            partition by account_id, amount, transaction_date
        ) as dup_group_size,
        row_number() over(
            partition by account_id, amount, transaction_date
            order by created_at
        ) as dup_rank
    from base
)

select  
    *,
    dup_group_size >  1 as is_likely_duplicate,
    dup_rank > 1 as is_duplicate_secondary
from flagged
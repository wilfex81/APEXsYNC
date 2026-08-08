with expense_summary as (
    select * from {{ ref('mart_expense_summary') }}
),

category_trend as (
    select
        account_id,
        category,
        month,
        total_amount,
        avg(total_amount) over (
            partition by account_id, category
            order by month
            rows between 5 preceding and current row
        ) as rolling_6mo_avg,
        lag(total_amount, 1) over (
            partition by account_id, category
            order by month
        ) as prev_month_amount
    from expense_summary
),

flagged as (
    select
        account_id,
        category,
        month,
        total_amount,
        rolling_6mo_avg,
        case
            when rolling_6mo_avg > 0
                then (total_amount - rolling_6mo_avg) / rolling_6mo_avg
            else null
        end as pct_above_rolling_avg
    from category_trend
)

select
    account_id,
    category,
    month,
    total_amount,
    rolling_6mo_avg,
    round(pct_above_rolling_avg::numeric, 3) as pct_above_rolling_avg,
    pct_above_rolling_avg > 0.30 as is_cost_spike,
    case
        when pct_above_rolling_avg > 0.30 then
            'Category spend ' || round((pct_above_rolling_avg * 100)::numeric, 1) || '% above 6-month rolling average — review for waste'
        else null
    end as flag_reason
from flagged
where pct_above_rolling_avg > 0.30
order by month, pct_above_rolling_avg desc
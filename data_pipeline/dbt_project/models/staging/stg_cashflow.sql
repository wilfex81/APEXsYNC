with source as (

    select * from {{ source('core', 'core_cashflowevent') }}

),

renamed as (
    select 
        id                  as cashflow_event_id,
        entity_id,
        date                as  event_date,
        event_type,
        amount,
        projected
    from source
)

select * from renamed
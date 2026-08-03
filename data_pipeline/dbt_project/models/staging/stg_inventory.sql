with source as (
    select * from  {{ source('core', 'core_inventorysnapshot') }}
),

renamed as (

    select 
        id                      as snapshot_id,
        entity_id,
        sku,
        date                    as snapshot_date,
        qty                     as quantity,
        unit_cost,
        turnover_rate
    
    from source
)

select * from renamed
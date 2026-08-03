with source as (

    select * from  {{ source('core', 'core_transaction') }}

),

renamed as (

    select 
        id              as transaction_id,
        account_id,
        category_id,
        date            as transaction_date,
        amount,
        description,
        source_doc_ref,
        is_duplicate_flag,
        confidence_score,
        created_at
    from source

)

select * from renamed
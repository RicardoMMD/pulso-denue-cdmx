{{ config(post_hook=["create unique index on {{ this }} (edicion, id_denue)"]) }}

-- Identidad estable de cada establecimiento a través de las ediciones: sigue la cadena de vínculos
-- desde su alta (método 'ninguno' o 'id_reusado') hasta la última edición donde aparece.
with recursive cadena as (
    select edicion, id_denue, edicion as raiz_edicion, id_denue as raiz_id
    from {{ ref('vinculo_edicion') }}
    where metodo in ('ninguno', 'id_reusado')
    union all
    select v.edicion, v.id_denue, c.raiz_edicion, c.raiz_id
    from cadena c
    join {{ ref('vinculo_edicion') }} v
      on v.edicion_previa = c.edicion and v.id_previo = c.id_denue
),

raices as (
    select raiz_edicion, raiz_id,
           row_number() over (order by raiz_edicion, raiz_id)::int as sk_entidad
    from (select distinct raiz_edicion, raiz_id from cadena) r
)

select c.edicion, c.id_denue, r.sk_entidad
from cadena c
join raices r using (raiz_edicion, raiz_id)

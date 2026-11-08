{{ config(post_hook=[
    "create index on {{ this }} (edicion, id_denue)",
    "create index on {{ this }} (sk_conglomerado)",
    "create unique index on {{ this }} (edicion, id_denue) where es_principal"
]) }}

-- Puente establecimiento × conglomerado: un establecimiento puede pertenecer a varios (una tienda de un
-- mercado público que además está dentro de una zona comercial de OSM). es_principal marca uno por
-- establecimiento y edición: el de menor prioridad, y entre iguales el de menor superficie.
-- Tianguis y mercados sobre ruedas (prioridad 5 y 6) son actividad temporal junto a comercios permanentes:
-- quedan en el puente pero nunca son el conglomerado principal.
with campo as (
    select m.edicion, m.id_denue, c.sk_conglomerado, c.prioridad, c.superficie_m2
    from {{ ref('conglomerado_campo_denue_miembro') }} m
    join {{ ref('dim_conglomerado') }} c
      on c.clave_natural = 'denue:' || m.tipo_denue || '|' || m.nombre_norm || '|' || m.grupo
),

espacial as (
    select d.edicion, d.id_denue, c.sk_conglomerado, c.prioridad, c.superficie_m2
    from {{ ref('denue_valido') }} d
    join {{ ref('dim_conglomerado') }} c
      on c.metodo_asignacion = 'espacial' and st_covers(c.geom_utm, d.geom_utm)
),

todos as (
    select * from campo
    union all
    select * from espacial
)

select
    edicion, id_denue, sk_conglomerado,
    (prioridad <= 4
     and row_number() over (partition by edicion, id_denue order by prioridad, superficie_m2, sk_conglomerado) = 1) as es_principal
from todos

{{ config(post_hook=["create index on {{ this }} using gist (geom_utm)"]) }}

-- Alcaldías del DENUE, con su límite oficial (Marco Geoestadístico 2020 de INEGI) y su población (Censo 2020).
with nombres as (
    select distinct on (cve_municipio) cve_entidad, cve_municipio, municipio
    from {{ ref('denue_valido') }}
    order by cve_municipio, ordinal desc
),

geometria as (
    select cve_municipio, geom_utm from {{ ref('stg_mg2020_alcaldia') }}
)

select
    row_number() over (order by n.cve_municipio)::int as sk_alcaldia,
    n.cve_entidad, n.cve_municipio, n.municipio as nombre_alcaldia,
    p.poblacion                                     as poblacion_2020,
    g.geom_utm
from nombres n
left join geometria g using (cve_municipio)
left join {{ ref('stg_censo2020_alcaldia') }} p using (cve_municipio)

{{ config(post_hook=["create index on {{ this }} using gist (geom_utm)"]) }}

-- Colonias del catálogo de datos abiertos CDMX, más miembros especiales sin geometría:
--   0              "sin colonia" (alcaldía desconocida)
--   -<cve_mun>     "sin colonia (<alcaldía>)": establecimientos fuera del catálogo de colonias, en zonas
--                  rurales o sin colonia catalogada, de los que solo se sabe la alcaldía (p. ej. -13 = Xochimilco)
-- es_especial distingue los miembros especiales de las colonias reales.
select
    row_number() over (order by c.cve_col)::int as sk_colonia,
    c.cve_col, c.colonia, c.clasificacion,
    a.sk_alcaldia, c.cve_municipio, c.alcaldia,
    false                                       as es_especial,
    st_area(c.geom_utm)                         as area_m2,
    c.geom, c.geom_utm
from {{ ref('stg_colonias') }} c
left join {{ ref('dim_alcaldia') }} a on a.cve_municipio = c.cve_municipio
union all
select
    -(a.cve_municipio::int), null, 'sin colonia (' || a.nombre_alcaldia || ')', null,
    a.sk_alcaldia, a.cve_municipio, a.nombre_alcaldia, true, null, null, null
from {{ ref('dim_alcaldia') }} a
union all
select 0, null, 'sin colonia', null, null, null, null, true, null, null, null

{{ config(post_hook=["create index on {{ this }} (sk_colonia)", "create index on {{ this }} using gist (punto_utm)"]) }}

-- Población del Censo 2020 en la unidad más fina con ubicación: manzana urbana (con su polígono del Marco
-- Geoestadístico 2020) o localidad rural (punto de ITER). Cada unidad se asigna a una colonia del catálogo CDMX
-- por un punto interior: dentro del polígono, o la colonia más cercana a 100 m o menos, o el miembro
-- "sin colonia (<alcaldía>)". Sirve para población y densidad por colonia.
-- Queda fuera la población de localidades de una y dos viviendas (684 personas), sin ubicación; los totales por
-- alcaldía usan el total oficial de ITER (dim_alcaldia.poblacion_2020).
with manzanas as (
    select 'manzana'::text as tipo_unidad, c.cve_manzana as cve_unidad, c.cve_municipio, c.cve_ageb,
           c.poblacion, c.poblacion_0_14, c.poblacion_15_64, c.poblacion_65_mas, c.hogares, c.viviendas_habitadas,
           c.viviendas_con_internet, c.escolaridad_promedio, m.punto_utm
    from {{ ref('stg_censo2020_manzana') }} c
    join {{ ref('stg_mg2020_manzana') }} m using (cve_manzana)
),

rurales as (
    -- localidades sin manzanas en el Censo por manzana: rurales no amanzanadas
    select 'localidad rural', l.cve_localidad, l.cve_municipio, null::text,
           l.poblacion, null::int, null::int, null::int, null::int, null::int, null::int, null::numeric, l.punto_utm
    from {{ ref('stg_censo2020_localidad') }} l
    where not exists (select 1 from {{ ref('stg_censo2020_manzana') }} c where left(c.cve_manzana, 9) = l.cve_localidad)
),

unidades as (
    select * from manzanas
    union all
    select * from rurales
),

colonias as (
    select sk_colonia, geom_utm, area_m2 from {{ ref('dim_colonia') }} where not es_especial
)

select
    u.*,
    coalesce(dentro.sk_colonia, cerca.sk_colonia, especial.sk_colonia, 0)  as sk_colonia,
    case when dentro.sk_colonia is not null then 'poligono'
         when cerca.sk_colonia is not null then 'cercania'
         else 'ninguna' end                                                 as metodo_colonia
from unidades u
left join lateral (
    select sk_colonia from colonias c where st_covers(c.geom_utm, u.punto_utm) order by c.area_m2 limit 1
) dentro on true
left join lateral (
    select sk_colonia from colonias c
    where dentro.sk_colonia is null and st_dwithin(c.geom_utm, u.punto_utm, 100)
    order by c.geom_utm <-> u.punto_utm limit 1
) cerca on true
left join {{ ref('dim_colonia') }} especial on especial.es_especial and especial.sk_colonia = -(u.cve_municipio::int)

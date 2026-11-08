{{ config(post_hook=[
    "create index on {{ this }} using gin (nombre_norm gin_trgm_ops)",
    "create index on {{ this }} using gist (geom)"
]) }}

-- Catálogo de territorios para resolver lugares ("la Roma", "Iztapalapa"): la ciudad, sus 16 alcaldías y las
-- colonias del catálogo CDMX (incluye pueblos y barrios originarios). nombre_norm va en mayúsculas y sin acentos
-- para buscar con similarity(). Los miembros "sin colonia" no se listan.
-- poblacion_2020: Censo 2020. Ciudad y alcaldías, total oficial (ITER); colonias, suma de sus manzanas y localidades
-- rurales (poblacion_unidad). La población fuera del catálogo de colonias (zonas rurales) no se reparte.
with alcaldias as (
    select
        'alcaldia'::text                                         as nivel,
        cve_municipio                                            as cve_territorio,
        nombre_alcaldia                                          as nombre,
        cve_municipio,
        nombre_alcaldia                                          as alcaldia,
        null::text                                               as clasificacion,
        poblacion_2020,
        geom_utm
    from {{ ref('dim_alcaldia') }}
),

poblacion_colonia as (
    select sk_colonia, sum(poblacion)::int as poblacion from {{ ref('poblacion_unidad') }} group by 1
),

colonias as (
    select
        'colonia', c.cve_col, c.colonia, c.cve_municipio, c.alcaldia, c.clasificacion,
        coalesce(p.poblacion, 0), c.geom_utm
    from {{ ref('dim_colonia') }} c
    left join poblacion_colonia p using (sk_colonia)
    where not c.es_especial
),

ciudad as (
    select 'ciudad'::text as nivel, '09'::text as cve_territorio, 'Ciudad de México'::text as nombre,
           null::text as cve_municipio, null::text as alcaldia, null::text as clasificacion,
           sum(poblacion_2020)::int as poblacion_2020, st_union(geom_utm) as geom_utm
    from {{ ref('dim_alcaldia') }}
),

todos as (
    select * from ciudad
    union all select * from alcaldias
    union all select * from colonias
)

select
    nivel,
    cve_territorio,
    nombre,
    upper(unaccent(nombre))                                      as nombre_norm,
    cve_municipio,
    alcaldia,
    clasificacion,
    round((st_area(geom_utm) / 1e6)::numeric, 3)                 as area_km2,
    poblacion_2020,
    round((poblacion_2020 / nullif(st_area(geom_utm) / 1e6, 0))::numeric, 0) as densidad_hab_km2,
    st_y(st_transform(st_pointonsurface(geom_utm), 4326))        as latitud_centro,
    st_x(st_transform(st_pointonsurface(geom_utm), 4326))        as longitud_centro,
    st_transform(geom_utm, 4326)::geography                      as geom
from todos

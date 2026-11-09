{{ config(post_hook=[
    "create index on {{ this }} using gin (nombre_norm gin_trgm_ops)",
    "create index on {{ this }} (tipo, nombre_norm)",
    "create index on {{ this }} using gist (geom)"
]) }}

-- Catálogo único para resolver lugares (herramienta "Resolver lugar" del Analista, prototipo 3).
-- Una fila por lugar nombrable: la ciudad, alcaldías, colonias, estaciones del Metro, conglomerados (mercados,
-- plazas, centrales, tianguis) y calles (una por alcaldía donde la calle tiene establecimientos).
-- nombre_norm va en mayúsculas, sin acentos ni puntuación. peso sirve para desempatar (población, locales,
-- establecimientos). geom es un punto representativo; para "cerca de" usar ST_DWithin(geom, punto, metros).
with vigente as (
    select edicion from {{ ref('edicion') }} where es_vigente
),

territorios as (
    select nivel as tipo, cve_territorio as clave, nombre, nombre_norm, cve_municipio, alcaldia,
           clasificacion as detalle, coalesce(poblacion_2020, 0)::numeric as peso,
           latitud_centro as latitud, longitud_centro as longitud
    from {{ ref('territorio') }}
),

estaciones as (
    select 'estacion_metro'::text, e.estacion_norm, e.estacion, e.estacion_norm, null::text, null::text,
           array_to_string(e.lineas, ', '), e.num_lineas::numeric,
           st_y(st_transform(st_centroid(e.geom_utm), 4326)), st_x(st_transform(st_centroid(e.geom_utm), 4326))
    from {{ ref('dim_estacion_metro') }} e
),

conglomerados as (
    select 'conglomerado'::text, c.clave_conglomerado, c.nombre,
           regexp_replace(upper(unaccent(c.nombre)), '[^A-Z0-9 ]', ' ', 'g'), c.cve_municipio, c.alcaldia,
           c.tipo, coalesce(c.num_locales, c.establecimientos, 0)::numeric, c.latitud_centro, c.longitud_centro
    from {{ ref('conglomerado') }} c, vigente v
    where c.edicion = v.edicion and c.nombre is not null and c.latitud_centro is not null
),

centro_calle as (
    select x.cve_municipio, x.calle_norm, avg(x.latitud) as latitud, avg(x.longitud) as longitud
    from {{ ref('establecimiento') }} x
    join vigente v on v.edicion = x.edicion
    where x.calle_norm is not null
    group by 1, 2
),

calles as (
    select 'calle'::text, c.cve_municipio || ':' || c.calle_norm, c.calle, c.calle_norm, c.cve_municipio, c.alcaldia,
           null::text, c.establecimientos::numeric, p.latitud, p.longitud
    from {{ ref('calle') }} c
    join vigente v on v.edicion = c.edicion
    join centro_calle p on p.cve_municipio = c.cve_municipio and p.calle_norm = c.calle_norm
    where c.establecimientos >= 5
),

todos as (
    select * from territorios
    union all select * from estaciones
    union all select * from conglomerados
    union all select * from calles
)

select
    tipo, clave, nombre,
    trim(regexp_replace(regexp_replace(upper(unaccent(nombre_norm)), '[^A-Z0-9 ]', ' ', 'g'), '\s+', ' ', 'g')) as nombre_norm,
    cve_municipio, alcaldia, detalle, peso, latitud, longitud,
    st_setsrid(st_makepoint(longitud, latitud), 4326)::geography as geom
from todos
where latitud is not null and longitud is not null

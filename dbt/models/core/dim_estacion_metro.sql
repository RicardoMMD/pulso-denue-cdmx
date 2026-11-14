{{ config(post_hook=["create index on {{ this }} using gist (geom_utm)", "create unique index on {{ this }} (estacion_norm)"]) }}

-- Estaciones del Metro (STC), una por estación física: las de correspondencia agrupan sus líneas.
-- La ubicación es el centro de sus paradas en OpenStreetMap. Fuente: stg_metro.
-- en_cdmx: la estación cae dentro de una alcaldía (Marco Geoestadístico 2020). Las del Estado de México (Línea B
-- de Múzquiz a Ciudad Azteca, Línea A en La Paz y Los Reyes, Cuatro Caminos) solo tienen alrededor negocios del
-- lado de la Ciudad, porque el DENUE que cargamos es solo de CDMX: sus cifras están truncadas.
with estaciones as (
    select
        estacion_norm,
        mode() within group (order by estacion)                               as estacion,
        array_agg(distinct linea order by linea)                              as lineas,
        count(distinct cve_linea)                                             as num_lineas,
        st_centroid(st_collect(parada_utm))::geometry(point, 32614)           as geom_utm
    from {{ ref('stg_metro') }}
    group by estacion_norm
)

select
    e.estacion_norm,
    e.estacion,
    e.lineas,
    e.num_lineas,
    a.cve_municipio,
    a.nombre_alcaldia,
    a.cve_municipio is not null                                               as en_cdmx,
    e.geom_utm
from estaciones e
left join lateral (
    select cve_municipio, nombre_alcaldia
    from {{ ref('dim_alcaldia') }} al
    where st_intersects(al.geom_utm, e.geom_utm)
    order by cve_municipio
    limit 1
) a on true

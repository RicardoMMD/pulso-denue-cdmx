{{ config(post_hook=["create index on {{ this }} using gist (geom_utm)", "create unique index on {{ this }} (estacion_norm)"]) }}

-- Estaciones del Metro (STC), una por estación física: las de correspondencia agrupan sus líneas.
-- La ubicación es el centro de sus paradas en OpenStreetMap. Fuente: stg_metro.
select
    estacion_norm,
    mode() within group (order by estacion)                                   as estacion,
    array_agg(distinct linea order by linea)                                  as lineas,
    count(distinct cve_linea)                                                 as num_lineas,
    st_centroid(st_collect(parada_utm))::geometry(point, 32614)               as geom_utm
from {{ ref('stg_metro') }}
group by estacion_norm

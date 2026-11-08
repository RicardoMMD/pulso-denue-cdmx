-- Áreas comerciales de OpenStreetMap, geometría válida en UTM 14N. Los puntos se dejan como puntos.
select
    osm_tipo, osm_id, categoria,
    nullif(trim(nombre), '')                        as nombre,
    st_geometrytype(geom) = 'ST_Point'              as es_punto,
    st_transform(case when st_geometrytype(geom) = 'ST_Point' then geom else st_makevalid(geom) end, 32614) as geom_utm
from {{ source('raw', 'osm_comercio') }}

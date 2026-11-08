-- Calles de OpenStreetMap con nombre normalizado y geometría en UTM 14N.
select
    osm_id,
    highway                                              as tipo_via,
    nombre,
    {{ normalizar_vialidad('nombre') }}                  as nombre_norm,
    etiquetas ->> 'oneway'                               as sentido_unico,
    etiquetas ->> 'maxspeed'                             as velocidad_max,
    nodos,
    geom,
    st_transform(geom, 32614)::geometry(linestring, 32614) as geom_utm
from {{ source('raw', 'osm_calles') }}

-- Estaciones de cada línea en orden de recorrido (para el tren de luz que enciende negocios estación por estación).
-- Grano: línea × estación. Une con metro_estacion por estacion_norm para las cifras.
select
    m.linea,
    m.cve_linea,
    m.orden,
    e.estacion,
    m.estacion_norm,
    array_to_string(e.lineas, ', ')                                  as lineas_en_estacion,
    st_y(st_transform(e.geom_utm, 4326))                             as latitud,
    st_x(st_transform(e.geom_utm, 4326))                             as longitud
from {{ ref('stg_metro') }} m
join {{ ref('dim_estacion_metro') }} e using (estacion_norm)

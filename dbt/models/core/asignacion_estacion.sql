{{ config(post_hook=["create index on {{ this }} (edicion, id_denue)", "create index on {{ this }} (estacion_norm)"]) }}

-- Establecimientos a 800 m o menos (línea recta) de cada estación del Metro, por edición.
-- Un establecimiento puede estar cerca de varias estaciones; es_mas_cercana marca una sola por establecimiento,
-- para no contarlo dos veces en rankings de estaciones. Las vistas de línea usan la unión de radios (todas las filas).
-- Radios de la escena: 300, 500 (predeterminado) y 800 m. Segunda etapa: distancia por red peatonal.
select
    d.edicion,
    d.id_denue,
    e.estacion_norm,
    round(st_distance(d.geom_utm, e.geom_utm)::numeric, 1)                     as distancia_m,
    row_number() over (partition by d.edicion, d.id_denue
                       order by st_distance(d.geom_utm, e.geom_utm), e.estacion_norm) = 1 as es_mas_cercana
from {{ ref('denue_valido') }} d
join {{ ref('dim_estacion_metro') }} e on st_dwithin(d.geom_utm, e.geom_utm, 800)

{{ config(post_hook=["create unique index on {{ this }} (edicion, id_denue)"]) }}

-- Tramo de calle de cada establecimiento y edición (ver asignacion_tramo_punto).
select
    d.edicion, d.id_denue, a.sk_tramo, a.metodo_tramo, a.distancia_m
from {{ ref('denue_valido') }} d
join {{ ref('asignacion_tramo_punto') }} a
  on a.x = round(st_x(d.geom_utm)::numeric, 2)
 and a.y = round(st_y(d.geom_utm)::numeric, 2)
 and a.vialidad_norm is not distinct from
     {{ vialidad_denue_norm('d.vialidad') }}

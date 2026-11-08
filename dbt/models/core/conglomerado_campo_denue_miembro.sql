{{ config(post_hook=["create unique index on {{ this }} (edicion, id_denue)"]) }}

-- Pertenencia por campo DENUE: cada establecimiento (por edición) con su grupo de conglomerado.
select d.edicion, d.id_denue, p.tipo_denue, p.nombre_norm, p.grupo
from {{ ref('denue_valido') }} d
join {{ ref('conglomerado_campo_denue_puntos') }} p
  on p.tipo_denue = d.tipo_centro_comercial
 and p.nombre_norm = upper(regexp_replace(unaccent(trim(d.centro_comercial)), '\s+', ' ', 'g'))
 and p.x = round(st_x(d.geom_utm)::numeric, 2)
 and p.y = round(st_y(d.geom_utm)::numeric, 2)

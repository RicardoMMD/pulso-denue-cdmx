-- Conglomerados declarados en el DENUE con al menos 3 establecimientos en alguna edición.
-- Geometría: envolvente convexa de todos sus puntos (todas las ediciones) con 15 m de margen.
with por_edicion as (
    select tipo_denue, nombre_norm, grupo, edicion, count(*) as n
    from {{ ref('conglomerado_campo_denue_miembro') }}
    group by 1, 2, 3, 4
),

tamano as (
    select tipo_denue, nombre_norm, grupo, max(n) as n_max, count(*) as ediciones
    from por_edicion
    group by 1, 2, 3
    having max(n) >= 3
),

forma as (
    select tipo_denue, nombre_norm, grupo,
           st_buffer(st_convexhull(st_collect(st_setsrid(st_makepoint(x, y), 32614))), 15) as geom_utm
    from {{ ref('conglomerado_campo_denue_puntos') }}
    group by 1, 2, 3
)

select t.tipo_denue, t.nombre_norm, t.grupo, t.n_max, t.ediciones, f.geom_utm
from tamano t
join forma f using (tipo_denue, nombre_norm, grupo)

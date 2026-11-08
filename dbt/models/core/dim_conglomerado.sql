{{ config(post_hook=["create index on {{ this }} using gist (geom_utm)", "create unique index on {{ this }} (clave_natural)"]) }}

-- Conglomerados comerciales y de equipamiento de todas las fuentes (ver conglomerado_fuente), más el miembro 0.
-- num_locales: máximo de establecimientos en una edición (campo DENUE), locales del padrón u oferentes (tianguis).
select
    row_number() over (order by prioridad, tipo, nombre, clave_natural)::int as sk_conglomerado,
    clave_natural, tipo, categoria, nombre, alcaldia, origen, metodo_asignacion, prioridad,
    num_locales,
    round(st_area(geom_utm)::numeric, 0)                      as superficie_m2,
    round(sqrt(st_area(geom_utm) / pi())::numeric, 1)         as radio_equivalente_m,
    st_transform(st_pointonsurface(geom_utm), 4326)::geometry(point, 4326) as geom_centro,
    geom_utm::geometry(geometry, 32614)
from {{ ref('conglomerado_fuente') }}
union all
select 0, 'sin asignar', 'sin asignar', null, 'sin asignar', null, null, null, null, null, null, null, null, null

{{ config(post_hook=["create index on {{ this }} using gist (geom_utm)", "create index on {{ this }} (nombre_norm)"]) }}

-- Tramos de calle (cuadras) de OpenStreetMap dentro de CDMX, más el miembro 0 "sin asignar".
-- Colonia del tramo: la que contiene su punto medio.
select
    row_number() over (order by t.osm_id, t.idx_tramo)::int as sk_tramo,
    t.osm_id,
    t.idx_tramo,
    c.nombre                                  as nombre_vialidad,
    c.nombre_norm,
    c.tipo_via,
    c.sentido_unico,
    c.velocidad_max,
    round(st_length(t.geom_utm)::numeric, 1)  as longitud_m,
    col.sk_colonia,
    col.colonia,
    st_transform(t.geom_utm, 4326)::geometry(linestring, 4326) as geom,
    t.geom_utm
from {{ ref('tramo_corte') }} t
join {{ ref('stg_osm_calles') }} c using (osm_id)
cross join lateral (
    select sk_colonia, colonia
    from {{ ref('dim_colonia') }} c2
    where c2.sk_colonia > 0 and st_covers(c2.geom_utm, st_lineinterpolatepoint(t.geom_utm, 0.5))
    order by c2.area_m2
    limit 1
) col
union all
select 0, null, null, 'sin asignar', null, null, null, null, null, null, null, null, null

{{ config(materialized='table') }}

-- Cuadras: cada calle de OSM se corta en sus nodos compartidos con otra calle (cruces) y en sus extremos.
-- Un tramo va de un cruce al siguiente. Solo se conservan los tramos cuyo punto medio cae en una colonia de CDMX.
with puntos as (
    select c.osm_id, p.ord::int as ord, c.nodos[p.ord] as nodo, st_pointn(c.geom_utm, p.ord::int) as pt,
           cardinality(c.nodos) as n
    from {{ ref('stg_osm_calles') }} c
    cross join lateral generate_series(1, cardinality(c.nodos)) as p(ord)
    where cardinality(c.nodos) = st_npoints(c.geom_utm)
),

compartidos as (
    select nodo from puntos group by nodo having count(distinct osm_id) >= 2
),

marcados as (
    select p.*, (p.ord = 1 or p.ord = p.n or cp.nodo is not null) as es_corte
    from puntos p
    left join compartidos cp using (nodo)
),

tramos_idx as (
    -- cada punto pertenece al tramo iniciado por el último corte hasta él; un corte también cierra el anterior
    select osm_id, ord, pt,
           sum(es_corte::int) over (partition by osm_id order by ord) as tramo
    from marcados
),

membresia as (
    select osm_id, ord, pt, tramo from tramos_idx
    union all
    select m.osm_id, m.ord, m.pt, t.tramo - 1
    from marcados m
    join tramos_idx t on t.osm_id = m.osm_id and t.ord = m.ord
    where m.es_corte and m.ord > 1
),

lineas as (
    select osm_id, tramo,
           st_makeline(pt order by ord) as geom_utm
    from membresia
    group by osm_id, tramo
    having count(*) >= 2
)

select osm_id, tramo as idx_tramo, geom_utm::geometry(linestring, 32614)
from lineas
where st_geometrytype(geom_utm) = 'ST_LineString' and st_length(geom_utm) > 1

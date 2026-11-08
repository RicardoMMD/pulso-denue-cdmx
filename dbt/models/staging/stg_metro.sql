-- Metro de CDMX (STC) desde OpenStreetMap: una fila por línea y estación, con el orden de la estación en la línea.
-- Por cada línea se toma el sentido con más paradas; las paradas son los nodos miembros con rol stop (o
-- platform) y nombre. La estación se identifica por su nombre normalizado (las de correspondencia lo comparten).
with relaciones as (
    select osm_id, etiquetas ->> 'ref' as linea, etiquetas ->> 'name' as nombre_ruta, miembros
    from {{ source('raw', 'osm_metro') }}
    where osm_tipo = 'relation' and etiquetas ->> 'network' = 'STC Metro'
),

nodos as (
    select osm_id, etiquetas, geom from {{ source('raw', 'osm_metro') }} where osm_tipo = 'node'
),

paradas as (
    select r.linea, r.osm_id as osm_id_ruta, m.ord, n.etiquetas ->> 'name' as nombre, n.geom
    from relaciones r
    cross join lateral jsonb_array_elements(r.miembros) with ordinality as m(miembro, ord)
    join nodos n on n.osm_id = (m.miembro ->> 'ref')::bigint
    where m.miembro ->> 'type' = 'node'
      and m.miembro ->> 'role' in ('stop', 'stops', 'stop_entry_only', 'stop_exit_only', 'platform')
      and n.etiquetas ->> 'name' is not null
),

por_ruta as (
    select linea, osm_id_ruta, count(distinct nombre) as n_estaciones,
           row_number() over (partition by linea order by count(distinct nombre) desc, osm_id_ruta) as rn
    from paradas
    group by 1, 2
),

estaciones_linea as (
    -- primera aparición de cada estación en la ruta elegida, para el orden
    select distinct on (p.linea, upper(unaccent(p.nombre_limpio)))
        p.linea, p.nombre_limpio as nombre, upper(unaccent(p.nombre_limpio)) as nombre_norm, p.ord, p.geom
    from (
        -- OSM distingue las estaciones de correspondencia por línea ("Candelaria L1", "Tacubaya (Línea 7)")
        select *, trim(regexp_replace(nombre, '\s+(L[0-9AB]+|\(Línea [0-9AB]+\))$', '')) as nombre_limpio
        from paradas
    ) p
    join por_ruta r on r.osm_id_ruta = p.osm_id_ruta and r.rn = 1
    order by p.linea, upper(unaccent(p.nombre_limpio)), p.ord
)

select
    'Línea ' || linea                                                       as linea,
    linea                                                                   as cve_linea,
    row_number() over (partition by linea order by ord)::int                as orden,
    nombre                                                                  as estacion,
    nombre_norm                                                             as estacion_norm,
    st_transform(geom, 32614)::geometry(point, 32614)                       as parada_utm
from estaciones_linea

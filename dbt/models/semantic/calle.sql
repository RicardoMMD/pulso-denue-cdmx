{{ config(post_hook=["create index on {{ this }} (edicion, cve_municipio)", "create index on {{ this }} using gin (calle_norm gin_trgm_ops)"]) }}

-- Calles y su giro (escena Las calles hablan). Grano: edición × alcaldía × calle (nombre normalizado de OSM).
-- Solo establecimientos con tramo de calle con nombre. giro_dominante es el subsector SCIAN más frecuente
-- en la calle y participacion_giro_dominante su peso. La calle se asignó por nombre, nombre parecido o cercanía
-- (columna metodo_tramo de establecimiento); por_cercania cuenta los asignados solo por cercanía.
with base as (
    select edicion, cve_municipio, alcaldia, calle_norm, calle, osm_id_calle, cve_subsector, nombre_subsector, metodo_tramo
    from {{ ref('establecimiento') }}
    where calle_norm is not null
),

por_giro as (
    select edicion, cve_municipio, calle_norm, cve_subsector, nombre_subsector, count(*) as n,
           row_number() over (partition by edicion, cve_municipio, calle_norm order by count(*) desc, cve_subsector) as rn
    from base
    group by 1, 2, 3, 4, 5
)

select
    b.edicion, b.cve_municipio, b.alcaldia, b.calle_norm,
    mode() within group (order by b.calle)                         as calle,
    count(*)                                                        as establecimientos,
    count(distinct b.osm_id_calle)                                  as vias_osm,
    count(*) filter (where b.metodo_tramo = 'cercania')             as por_cercania,
    g.cve_subsector                                                 as cve_giro_dominante,
    g.nombre_subsector                                              as giro_dominante,
    round(g.n::numeric / count(*), 3)                               as participacion_giro_dominante
from base b
join por_giro g on g.edicion = b.edicion and g.cve_municipio = b.cve_municipio and g.calle_norm = b.calle_norm and g.rn = 1
group by b.edicion, b.cve_municipio, b.alcaldia, b.calle_norm, g.cve_subsector, g.nombre_subsector, g.n

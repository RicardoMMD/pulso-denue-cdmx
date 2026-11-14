-- Vida comercial alrededor de cada estación del Metro (Corredores del Metro, modo ranking).
-- Grano: edición × estación × radio (300, 500 u 800 m en línea recta).
-- Cada establecimiento cuenta solo en su estación más cercana dentro del radio, para no contarlo dos veces
-- en rankings. Para la vista de línea (unión de radios) usar semantic.metro_linea.
-- Las estaciones fuera de la Ciudad (en_cdmx falso) conservan sus cifras, truncadas al lado de la Ciudad, pero no
-- entran al ranking: su lugar es nulo.
with radios as (
    select unnest(array[300, 500, 800]) as radio_m
),

base as (
    select a.edicion, a.estacion_norm, r.radio_m, x.cve_subsector, x.nombre_subsector, x.estrato_orden
    from {{ ref('asignacion_estacion') }} a
    join radios r on a.distancia_m <= r.radio_m
    join {{ ref('establecimiento') }} x on x.edicion = a.edicion and x.id_denue = a.id_denue
    where a.es_mas_cercana
),

giro as (
    select edicion, estacion_norm, radio_m, cve_subsector, nombre_subsector, count(*) as n,
           row_number() over (partition by edicion, estacion_norm, radio_m
                              order by count(*) desc, nombre_subsector) as rn
    from base
    group by 1, 2, 3, 4, 5
),

estaciones as (
    select
        b.edicion,
        e.estacion,
        e.estacion_norm,
        array_to_string(e.lineas, ', ')                                      as lineas,
        e.num_lineas,
        e.en_cdmx,
        e.nombre_alcaldia                                                    as alcaldia,
        b.radio_m,
        count(*)                                                             as establecimientos,
        count(*) filter (where b.estrato_orden <= 2)                         as micronegocios,
        g.nombre_subsector                                                   as giro_dominante,
        c.nombre_corto                                                       as giro_dominante_corto,
        round(g.n::numeric / count(*), 3)                                    as participacion_giro_dominante
    from base b
    join {{ ref('dim_estacion_metro') }} e using (estacion_norm)
    join giro g on g.edicion = b.edicion and g.estacion_norm = b.estacion_norm and g.radio_m = b.radio_m and g.rn = 1
    left join {{ ref('ref_subsector_corto') }} c on c.cve_subsector = g.cve_subsector
    group by b.edicion, e.estacion, e.estacion_norm, e.lineas, e.num_lineas, e.en_cdmx, e.nombre_alcaldia,
             b.radio_m, g.nombre_subsector, c.nombre_corto, g.n
)

select
    *,
    case when en_cdmx
         then rank() over (partition by edicion, radio_m, en_cdmx order by establecimientos desc) end as lugar
from estaciones

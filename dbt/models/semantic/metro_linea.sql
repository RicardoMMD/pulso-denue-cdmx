-- Vida comercial a lo largo de cada línea del Metro (Corredores del Metro, modo línea).
-- Grano: edición × línea × radio (300, 500 u 800 m). Cuenta cada establecimiento una vez por línea, si está
-- dentro del radio de cualquier estación de la línea (unión de radios). Un establecimiento cerca de una
-- correspondencia cuenta en ambas líneas, así que las líneas no se suman entre sí.
with radios as (
    select unnest(array[300, 500, 800]) as radio_m
),

lineas as (
    select distinct linea, cve_linea, estacion_norm from {{ ref('stg_metro') }}
)

select
    a.edicion,
    l.linea,
    l.cve_linea,
    r.radio_m,
    count(distinct a.id_denue)                                       as establecimientos,
    count(distinct l.estacion_norm)                                  as estaciones_con_negocios,
    (select count(*) from {{ ref('stg_metro') }} m where m.cve_linea = l.cve_linea) as estaciones,
    (select count(*) from {{ ref('stg_metro') }} m join {{ ref('dim_estacion_metro') }} e using (estacion_norm)
      where m.cve_linea = l.cve_linea and e.en_cdmx)                  as estaciones_en_cdmx
from {{ ref('asignacion_estacion') }} a
join lineas l using (estacion_norm)
join radios r on a.distancia_m <= r.radio_m
group by a.edicion, l.linea, l.cve_linea, r.radio_m

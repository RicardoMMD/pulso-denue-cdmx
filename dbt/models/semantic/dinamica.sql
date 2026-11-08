-- Altas, bajas y permanencias entre una edición y la anterior.
-- Grano: edición (desde la segunda) × alcaldía × macrosector.
--   permanecen   estaban en la edición anterior y siguen (mismo id o vínculo difuso)
--   nuevos       alta nueva: no estaban antes (incluye ids que INEGI reasignó a otro negocio)
--   reaparecen   faltaron en una o más ediciones y volvieron con el mismo id
--   bajas        estaban en la edición anterior y ya no aparecen; se cuentan con su alcaldía y
--                macrosector de la edición anterior
-- comparable_con_anterior = false (11/2024) avisa que el cambio mezcla crecimiento real con cambio de fuente
-- (incorporación del Censo Económico 2024 y paso a SCIAN 2023): no presentarlo como apertura o cierre de negocios.
with registros as (
    select f.sk_edicion, ed.edicion, f.id_denue, de.sk_entidad, al.cve_municipio, al.nombre_alcaldia,
           a.cve_macrosector, a.nombre_macrosector
    from {{ ref('fact_establecimiento') }} f
    join {{ ref('dim_edicion') }} ed on ed.sk_edicion = f.sk_edicion
    join {{ ref('dim_establecimiento') }} de on de.sk_establecimiento = f.sk_establecimiento
    join {{ ref('dim_ubicacion') }} u on u.sk_ubicacion = f.sk_ubicacion
    join {{ ref('dim_alcaldia') }} al on al.sk_alcaldia = u.sk_alcaldia
    join {{ ref('dim_actividad') }} a on a.sk_actividad = f.sk_actividad
),

entradas as (
    select r.sk_edicion, r.edicion, r.cve_municipio, r.nombre_alcaldia, r.cve_macrosector, r.nombre_macrosector,
           count(*) filter (where v.metodo in ('id', 'difuso'))            as permanecen,
           count(*) filter (where v.metodo in ('ninguno', 'id_reusado'))   as nuevos,
           count(*) filter (where v.metodo = 'id_salto')                   as reaparecen
    from registros r
    join {{ ref('vinculo_edicion') }} v on v.edicion = r.edicion and v.id_denue = r.id_denue
    where r.sk_edicion > 1
    group by 1, 2, 3, 4, 5, 6
),

salidas as (
    -- registros de la edición anterior cuya entidad no está en esta edición
    select p.sk_edicion + 1 as sk_edicion, p.cve_municipio, p.nombre_alcaldia, p.cve_macrosector, p.nombre_macrosector,
           count(*) as bajas
    from registros p
    where p.sk_edicion < (select max(sk_edicion) from {{ ref('dim_edicion') }})
      and not exists (select 1 from registros n where n.sk_edicion = p.sk_edicion + 1 and n.sk_entidad = p.sk_entidad)
    group by 1, 2, 3, 4, 5
)

select
    ed.edicion,
    ed.comparable_con_anterior,
    coalesce(e.cve_municipio, s.cve_municipio)             as cve_municipio,
    coalesce(e.nombre_alcaldia, s.nombre_alcaldia)         as alcaldia,
    coalesce(e.cve_macrosector, s.cve_macrosector)         as cve_macrosector,
    coalesce(e.nombre_macrosector, s.nombre_macrosector)   as nombre_macrosector,
    coalesce(e.permanecen, 0)                              as permanecen,
    coalesce(e.nuevos, 0)                                  as nuevos,
    coalesce(e.reaparecen, 0)                              as reaparecen,
    coalesce(s.bajas, 0)                                   as bajas,
    coalesce(e.nuevos, 0) + coalesce(e.reaparecen, 0) - coalesce(s.bajas, 0) as cambio_neto
from entradas e
full join salidas s
  on s.sk_edicion = e.sk_edicion and s.cve_municipio = e.cve_municipio and s.cve_macrosector = e.cve_macrosector
join {{ ref('dim_edicion') }} ed on ed.sk_edicion = coalesce(e.sk_edicion, s.sk_edicion)

{{ config(post_hook=["create index on {{ this }} using gin (nombre_clase_norm gin_trgm_ops)"]) }}

-- Catálogo de clases SCIAN presentes en el DENUE, por versión, con toda la jerarquía y su macrosector, para
-- traducir giros ("fonda", "tiendita") a clases. establecimientos_vigente cuenta la edición vigente.
-- Las ediciones desde 11/2024 usan SCIAN 2023; la 05/2024 usa SCIAN 2018.
select
    a.version_scian,
    a.clase_scian,
    a.nombre_clase,
    upper(unaccent(a.nombre_clase))                    as nombre_clase_norm,
    a.clase_scian_2023,
    a.cve_subrama,
    a.nombre_subrama,
    a.cve_rama,
    a.nombre_rama,
    a.cve_subsector,
    a.nombre_subsector,
    s.sector_agrupado                                  as cve_sector,
    s.nombre_sector,
    a.cve_macrosector,
    a.nombre_macrosector,
    count(f.*) filter (where f.sk_edicion = (select max(sk_edicion) from {{ ref('dim_edicion') }})) as establecimientos_vigente
from {{ ref('dim_actividad') }} a
join {{ ref('dim_scian_sector') }} s on s.sk_sector = a.sk_sector
left join {{ ref('fact_establecimiento') }} f on f.sk_actividad = a.sk_actividad
group by a.sk_actividad, a.version_scian, a.clase_scian, a.nombre_clase, a.clase_scian_2023, a.cve_subrama,
         a.nombre_subrama, a.cve_rama, a.nombre_rama, a.cve_subsector, a.nombre_subsector, s.sector_agrupado,
         s.nombre_sector, a.cve_macrosector, a.nombre_macrosector

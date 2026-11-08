{{ config(post_hook=["create index on {{ this }} (edicion, nivel, cve_territorio)", "create index on {{ this }} (edicion, clase_scian)"]) }}

-- Establecimientos por clase SCIAN en la ciudad y en cada alcaldía (escena Rarezas y rankings de giros).
-- Grano: edición × territorio (ciudad o alcaldía) × clase. Rarezas: establecimientos <= 3.
select
    edicion,
    case when cve_municipio is null then 'ciudad' else 'alcaldia' end   as nivel,
    coalesce(cve_municipio, '09')                                        as cve_territorio,
    coalesce(alcaldia, 'Ciudad de México')                               as territorio,
    version_scian, clase_scian, nombre_clase, cve_sector, cve_macrosector,
    count(*)                                                             as establecimientos
from {{ ref('establecimiento') }}
group by grouping sets (
    (edicion, version_scian, clase_scian, nombre_clase, cve_sector, cve_macrosector),
    (edicion, cve_municipio, alcaldia, version_scian, clase_scian, nombre_clase, cve_sector, cve_macrosector)
)

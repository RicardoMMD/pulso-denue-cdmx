{{ config(post_hook=["create index on {{ this }} (edicion, nivel, cve_territorio)"]) }}

-- Perfil sectorial de cada territorio (escenas El ADN de cada alcaldía y Colonias gemelas).
-- Grano: edición × territorio (alcaldía o colonia) × sector SCIAN (31-33 y 48-49 agrupados).
--   participacion           establecimientos del sector / establecimientos del territorio
--   cociente_localizacion   participación en el territorio / participación en la ciudad; > 1 = especialización
-- Las colonias excluyen los establecimientos sin colonia del catálogo.
with base as (
    select edicion, cve_municipio, alcaldia, cve_col, colonia, cve_sector, nombre_sector, cve_macrosector
    from {{ ref('establecimiento') }}
),

por_territorio as (
    select edicion, 'alcaldia'::text as nivel, cve_municipio as cve_territorio, alcaldia as territorio,
           cve_municipio, alcaldia, cve_sector, nombre_sector, cve_macrosector, count(*) as establecimientos
    from base
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9
    union all
    -- a nivel colonia, la alcaldía es la de la colonia en el catálogo (algunos establecimientos declaran otra)
    select b.edicion, 'colonia', b.cve_col, b.colonia, c.cve_municipio, c.alcaldia,
           b.cve_sector, b.nombre_sector, b.cve_macrosector, count(*)
    from base b
    join {{ ref('dim_colonia') }} c on c.cve_col = b.cve_col and not c.es_especial
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9
),

ciudad as (
    select edicion, cve_sector,
           count(*)::numeric / sum(count(*)) over (partition by edicion) as participacion_ciudad
    from base
    group by 1, 2
)

select
    t.edicion, t.nivel, t.cve_territorio, t.territorio, t.cve_municipio, t.alcaldia,
    t.cve_sector, t.nombre_sector, t.cve_macrosector,
    t.establecimientos,
    sum(t.establecimientos) over (partition by t.edicion, t.nivel, t.cve_territorio)          as establecimientos_territorio,
    round(t.establecimientos::numeric
          / sum(t.establecimientos) over (partition by t.edicion, t.nivel, t.cve_territorio), 4) as participacion,
    round(c.participacion_ciudad, 4)                                                         as participacion_ciudad,
    round(t.establecimientos::numeric
          / sum(t.establecimientos) over (partition by t.edicion, t.nivel, t.cve_territorio)
          / c.participacion_ciudad, 3)                                                       as cociente_localizacion
from por_territorio t
join ciudad c using (edicion, cve_sector)

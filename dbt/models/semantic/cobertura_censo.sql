-- ¿Cuánto se parece el DENUE al Censo Económico 2024? Para responder "qué tan completo es el DENUE".
-- Grano: edición × alcaldía × sector. razon = establecimientos DENUE / unidades del Censo.
-- Referencias distintas: el Censo es 2023 (levantado en 2024); las ediciones del DENUE van de 05/2024 a 05/2026.
select
    v.edicion,
    al.cve_municipio,
    v.nombre_alcaldia                 as alcaldia,
    v.sector_agrupado                 as cve_sector,
    v.nombre_sector,
    v.ue_denue                        as establecimientos_denue,
    v.ue_censo                        as unidades_censo,
    v.razon,
    v.diferencia,
    v.en_alcance_censo
from {{ ref('validacion_denue_censo') }} v
join {{ ref('dim_alcaldia') }} al on al.sk_alcaldia = v.sk_alcaldia

{{ config(severity='warn') }}
-- Aviso (no falla la construcción): en la edición más reciente, el total del DENUE por alcaldía,
-- en los sectores que cubre el Censo, no debe alejarse del Censo más de -10 % / +25 %.
-- Referencia al 2026-11-07: razón entre 1.06 y 1.11 en las 16 alcaldías.
with ultima as (select max(edicion) as edicion from {{ ref('dim_edicion') }}),
     por_alcaldia as (
        select v.nombre_alcaldia, sum(v.ue_denue) as ue_denue, sum(v.ue_censo) as ue_censo
        from {{ ref('validacion_denue_censo') }} v, ultima
        where v.edicion = ultima.edicion and v.en_alcance_censo
        group by 1)
select nombre_alcaldia, ue_denue, ue_censo, round(ue_denue / ue_censo, 3) as razon
from por_alcaldia
where ue_denue / ue_censo not between 0.90 and 1.25

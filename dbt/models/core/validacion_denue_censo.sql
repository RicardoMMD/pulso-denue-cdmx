-- ¿Cuánto se parece el DENUE al Censo Económico 2024? Establecimientos por edición × alcaldía × sector.
-- razon = unidades DENUE / unidades Censo. Cerca de 1 = coinciden; sobre 1 = el DENUE registra más.
-- Los sectores del DENUE que el Censo no cubre (gobierno, 93) salen con ue_censo nulo (en_alcance_censo = false).
-- Referencias distintas en el tiempo: el Censo es 2023 y se levantó en 2024; las ediciones del DENUE van de 05/2024 a 05/2026.
with censo as (
    select sk_alcaldia, cve_sector as sector_agrupado, ue as ue_censo
    from {{ ref('fact_censo_economico') }}
    where nivel_territorial = 'alcaldia' and nivel_actividad = 'sector' and tipo_estrato = 'suma'
),

denue as (
    select f.sk_edicion, u.sk_alcaldia, s.sector_agrupado, count(*) as ue_denue
    from {{ ref('fact_establecimiento') }} f
    join {{ ref('dim_ubicacion') }} u using (sk_ubicacion)
    join {{ ref('dim_actividad') }} a using (sk_actividad)
    join {{ ref('dim_scian_sector') }} s on s.sk_sector = a.sk_sector
    group by 1, 2, 3
)

select
    e.edicion,
    al.nombre_alcaldia,
    d.sk_alcaldia,
    d.sector_agrupado,
    s.nombre_sector,
    c.ue_censo,
    d.ue_denue,
    round(d.ue_denue / nullif(c.ue_censo, 0), 3)   as razon,
    d.ue_denue - c.ue_censo                        as diferencia,
    c.ue_censo is not null                         as en_alcance_censo
from denue d
join {{ ref('dim_edicion') }} e on e.sk_edicion = d.sk_edicion
join {{ ref('dim_alcaldia') }} al on al.sk_alcaldia = d.sk_alcaldia
left join (select distinct sector_agrupado, nombre_sector from {{ ref('dim_scian_sector') }}) s using (sector_agrupado)
left join censo c on c.sk_alcaldia = d.sk_alcaldia and c.sector_agrupado = d.sector_agrupado

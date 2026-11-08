-- Censos Económicos 2024 (año de referencia 2023, SCIAN 2023) por territorio y sector, con nombres legibles.
-- Grano: territorio (ciudad o alcaldía) × sector (o 'total'), suma de estratos.
-- Montos en millones de pesos. Una cifra nula es confidencial (INEGI no la publica); unidades siempre se publican.
-- El Censo no cubre el sector 93 (gobierno) ni el comercio ambulante.
select
    case when c.sk_alcaldia is null then 'ciudad' else 'alcaldia' end    as nivel,
    coalesce(a.cve_municipio, '09')                                       as cve_territorio,
    coalesce(a.nombre_alcaldia, 'Ciudad de México')                       as territorio,
    coalesce(c.cve_sector, 'total')                                       as cve_sector,
    coalesce(s.nombre_sector, 'Todos los sectores')                       as nombre_sector,
    c.ue                                                                  as unidades_economicas,
    c.h001a                                                               as personal_ocupado,
    c.j000a                                                               as remuneraciones_mdp,
    c.a111a                                                               as produccion_bruta_mdp,
    c.a131a                                                               as valor_agregado_mdp,
    c.a800a                                                               as ingresos_mdp,
    c.k000a                                                               as gastos_mdp,
    c.q000a                                                               as activos_fijos_mdp
from {{ ref('fact_censo_economico') }} c
left join {{ ref('dim_alcaldia') }} a on a.sk_alcaldia = c.sk_alcaldia
left join (select distinct sector_agrupado, nombre_sector from {{ ref('dim_scian_sector') }}) s
  on s.sector_agrupado = c.cve_sector
where c.tipo_estrato = 'suma'
  and c.nivel_actividad in ('total', 'sector')

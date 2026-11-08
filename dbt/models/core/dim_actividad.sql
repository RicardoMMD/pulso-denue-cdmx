-- Copo de nieve SCIAN: clase → subrama → rama → subsector → sector → macrosector del portal.
-- Grano: versión SCIAN × clase. El DENUE cambió de SCIAN 2018 a SCIAN 2023 a partir de 11/2024
-- (ver dim_edicion.version_scian). Un mismo código puede existir en ambas versiones con otro contenido,
-- así que cada versión tiene su fila y el hecho se une por (versión de la edición, clase).
-- Los códigos de cada nivel salen del prefijo de la clase.
-- Nombres: sector, de la seed; clase, del DENUE (edición más reciente de esa versión donde aparece);
-- subsector, rama y subrama, del catálogo de los Censos Económicos 2024, que es SCIAN 2023
-- (version_nombres_jerarquia). En las filas SCIAN 2018 esos nombres son aproximados donde 2023 reclasificó.
-- clase_scian_2023: clase en SCIAN 2023 para comparar ediciones a nivel de clase. Igual al código en las filas
-- 2023; en las 2018, la clase 2023 de la tabla comparativa de INEGI, o nula si la clase 2018 se reparte
-- entre varias clases 2023 (ver scian_correspondencia).
with clases as (
    select distinct on (version_scian, clase_scian)
        version_scian, clase_scian, nombre_actividad
    from {{ ref('denue_valido') }}
    order by version_scian, clase_scian, ordinal desc
),

destino_2023 as (
    select clase_2018, min(clase_2023) as clase_2023, count(*) as destinos
    from {{ ref('ref_scian_2023_2018') }}
    group by 1
),

catalogo as (
    select codigo, nombre from {{ ref('stg_ce_catalogo_actividad') }}
)

select
    row_number() over (order by c.version_scian, c.clase_scian)::int as sk_actividad,
    c.version_scian,
    c.clase_scian,
    case
        when c.version_scian = 'SCIAN 2023' then c.clase_scian
        when t.clase_2018 is null then c.clase_scian
        when t.destinos = 1 then t.clase_2023
    end                                             as clase_scian_2023,
    c.nombre_actividad                              as nombre_clase,
    left(c.clase_scian, 5)                          as cve_subrama,
    sr.nombre                                       as nombre_subrama,
    left(c.clase_scian, 4)                          as cve_rama,
    r.nombre                                        as nombre_rama,
    left(c.clase_scian, 3)                          as cve_subsector,
    ss.nombre                                       as nombre_subsector,
    s.sk_sector,
    left(c.clase_scian, 2)                          as cve_sector,
    s.nombre_sector,
    s.sk_macrosector,
    s.cve_macrosector,
    s.nombre_macrosector,
    'SCIAN 2023 (catálogo Censos Económicos 2024)'  as version_nombres_jerarquia
from clases c
left join destino_2023 t on c.version_scian = 'SCIAN 2018' and t.clase_2018 = c.clase_scian
left join {{ ref('dim_scian_sector') }} s on s.cve_sector = left(c.clase_scian, 2)
left join catalogo sr on sr.codigo = left(c.clase_scian, 5)
left join catalogo r on r.codigo = left(c.clase_scian, 4)
left join catalogo ss on ss.codigo = left(c.clase_scian, 3)

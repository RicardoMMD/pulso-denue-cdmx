-- Ficha de la ciudad y de cada alcaldía (fichas por alcaldía, La ciudad que brilla en línea).
-- Grano: edición × territorio (ciudad o alcaldía).
--   micronegocios: 0 a 10 personas ocupadas (los dos primeros estratos del DENUE)
--   presencia digital: declara sitio web o correo (mide lo declarado, no la presencia real)
--   nuevos / bajas: ver semantic.dinamica; nulos en la primera edición
--   establecimientos_por_mil_hab: con la población del Censo 2020 (no hay población más reciente por alcaldía);
--     las alcaldías centrales reciben población flotante que trabaja ahí, así que la razón es alta
with base as (
    select
        edicion,
        cve_municipio,
        alcaldia,
        count(*)                                                   as establecimientos,
        count(*) filter (where estrato_orden <= 2)                 as micronegocios,
        count(*) filter (where estrato_orden >= 6)                 as grandes_101_o_mas,
        count(*) filter (where tiene_web)                          as con_web,
        count(*) filter (where tiene_correo)                       as con_correo,
        count(*) filter (where tiene_telefono)                     as con_telefono,
        count(*) filter (where tiene_presencia_digital)            as con_presencia_digital,
        count(*) filter (where clave_conglomerado is not null)     as en_conglomerado,
        count(*) filter (where tipo_unidad = 'Semifijo')           as semifijos,
        count(distinct clase_scian)                                as clases_distintas
    from {{ ref('establecimiento') }}
    group by grouping sets ((edicion), (edicion, cve_municipio, alcaldia))
),

dinamica as (
    select edicion, cve_municipio, sum(nuevos + reaparecen) as nuevos, sum(bajas) as bajas
    from {{ ref('dinamica') }}
    group by grouping sets ((edicion), (edicion, cve_municipio))
)

select
    b.edicion,
    case when b.cve_municipio is null then 'ciudad' else 'alcaldia' end         as nivel,
    coalesce(b.cve_municipio, '09')                                              as cve_territorio,
    coalesce(b.alcaldia, 'Ciudad de México')                                     as territorio,
    b.establecimientos,
    p.poblacion_2020,
    round(1000.0 * b.establecimientos / nullif(p.poblacion_2020, 0), 1)       as establecimientos_por_mil_hab,
    round(b.establecimientos::numeric / sum(b.establecimientos) filter (where b.cve_municipio is null)
          over (partition by b.edicion), 4)                                      as participacion_ciudad,
    b.micronegocios,
    round(b.micronegocios::numeric / b.establecimientos, 4)                      as pct_micronegocios,
    b.grandes_101_o_mas,
    b.con_web,
    b.con_correo,
    b.con_telefono,
    b.con_presencia_digital,
    round(b.con_presencia_digital::numeric / b.establecimientos, 4)              as pct_presencia_digital,
    b.en_conglomerado,
    round(b.en_conglomerado::numeric / b.establecimientos, 4)                    as pct_en_conglomerado,
    b.semifijos,
    b.clases_distintas,
    d.nuevos,
    d.bajas,
    e.comparable_con_anterior
from base b
join {{ ref('dim_edicion') }} e on e.edicion = b.edicion
left join (
    select cve_municipio, poblacion_2020 from {{ ref('dim_alcaldia') }}
    union all
    select null, sum(poblacion_2020)::int from {{ ref('dim_alcaldia') }}
) p on p.cve_municipio is not distinct from b.cve_municipio
left join dinamica d on d.edicion = b.edicion and d.cve_municipio is not distinct from b.cve_municipio

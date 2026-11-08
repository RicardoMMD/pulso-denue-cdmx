{{ config(post_hook=[
    "create index on {{ this }} (edicion, cve_municipio)",
    "create index on {{ this }} (edicion, cve_col)",
    "create index on {{ this }} (edicion, clase_scian)",
    "create index on {{ this }} (edicion, cve_sector)",
    "create index on {{ this }} (edicion, clave_conglomerado)",
    "create index on {{ this }} (id_denue)",
    "create index on {{ this }} using gist (geom)",
    "create index on {{ this }} using gin (nombre gin_trgm_ops)"
]) }}

-- Un establecimiento por edición del DENUE, con todo lo que se pregunta de él en una sola fila.
-- Solo claves naturales (id DENUE, claves INEGI, cve_col, clave de conglomerado, osm_id): las llaves sustitutas
-- de core cambian en cada reconstrucción y no deben salir de la base.
with ediciones as (
    select sk_edicion, edicion, fecha_corte, version_scian,
           sk_edicion = min(sk_edicion) over () as es_primera,
           sk_edicion = max(sk_edicion) over () as es_vigente
    from {{ ref('dim_edicion') }}
)

select
    -- edición
    e.edicion,
    e.fecha_corte,
    e.es_vigente                                         as edicion_vigente,

    -- establecimiento
    f.id_denue,
    de.nombre,
    de.razon_social,
    de.tipo_unidad,
    s.estrato,
    s.orden                                              as estrato_orden,
    de.fecha_alta,
    de.edicion_alta,
    (de.edicion_alta = e.edicion and not e.es_primera)   as es_nuevo_en_edicion,

    -- actividad (SCIAN de la edición; clase_scian_2023 para comparar entre ediciones)
    a.version_scian,
    a.clase_scian,
    a.nombre_clase,
    a.clase_scian_2023,
    a.cve_rama,
    a.nombre_rama,
    a.cve_subsector,
    a.nombre_subsector,
    sc.sector_agrupado                                   as cve_sector,
    sc.nombre_sector,
    a.cve_macrosector,
    a.nombre_macrosector,

    -- territorio (alcaldía declarada por el DENUE; colonia del catálogo CDMX asignada por punto)
    al.cve_municipio,
    al.nombre_alcaldia                                   as alcaldia,
    c.cve_col,
    c.colonia,
    f.metodo_colonia,
    f.alcaldia_colonia,
    g.cve_ageb,
    u.cve_manzana,
    u.codigo_postal,
    u.colonia_denue,

    -- dirección declarada
    d.tipo_vialidad,
    d.vialidad,
    d.numero_exterior,
    d.tipo_centro_comercial,
    d.centro_comercial,

    -- calle (tramo de OpenStreetMap)
    t.osm_id                                             as osm_id_calle,
    t.nombre_vialidad                                    as calle,
    t.nombre_norm                                        as calle_norm,
    f.metodo_tramo,

    -- conglomerado principal
    nullif(cg.clave_natural, 'sin asignar')              as clave_conglomerado,
    case when cg.sk_conglomerado > 0 then cg.nombre end  as conglomerado,
    case when cg.sk_conglomerado > 0 then cg.tipo end    as tipo_conglomerado,

    -- Metro: estación más cercana a 800 m o menos (línea recta)
    me.estacion                                          as estacion_metro,
    am.distancia_m                                       as distancia_metro_m,

    -- contacto
    f.tiene_web,
    f.tiene_correo,
    f.tiene_telefono,
    (f.tiene_web or f.tiene_correo)                      as tiene_presencia_digital,
    de.telefono,
    de.correo,
    de.sitio_web,

    -- ubicación
    f.longitud,
    f.latitud,
    round(sqrt(f.x_m ^ 2 + f.y_m ^ 2)::numeric, 0)       as distancia_zocalo_m,
    f.geom,

    -- calidad
    f.texto_danado
from {{ ref('fact_establecimiento') }} f
join ediciones e on e.sk_edicion = f.sk_edicion
join {{ ref('dim_establecimiento') }} de on de.sk_establecimiento = f.sk_establecimiento
join {{ ref('dim_estrato') }} s on s.sk_estrato = f.sk_estrato
join {{ ref('dim_actividad') }} a on a.sk_actividad = f.sk_actividad
join {{ ref('dim_scian_sector') }} sc on sc.sk_sector = a.sk_sector
join {{ ref('dim_ubicacion') }} u on u.sk_ubicacion = f.sk_ubicacion
join {{ ref('dim_ageb') }} g on g.sk_ageb = u.sk_ageb
join {{ ref('dim_alcaldia') }} al on al.sk_alcaldia = u.sk_alcaldia
join {{ ref('dim_colonia') }} c on c.sk_colonia = f.sk_colonia
join {{ ref('dim_tramo') }} t on t.sk_tramo = f.sk_tramo
join {{ ref('dim_conglomerado') }} cg on cg.sk_conglomerado = f.sk_conglomerado
join {{ ref('denue_valido') }} d on d.edicion = e.edicion and d.id_denue = f.id_denue
left join {{ ref('asignacion_estacion') }} am on am.edicion = e.edicion and am.id_denue = f.id_denue and am.es_mas_cercana
left join {{ ref('dim_estacion_metro') }} me on me.estacion_norm = am.estacion_norm

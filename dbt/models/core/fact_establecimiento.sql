{{ config(post_hook=[
    "create index on {{ this }} (sk_edicion)",
    "create index on {{ this }} (sk_actividad)",
    "create index on {{ this }} (sk_ubicacion)",
    "create index on {{ this }} (sk_establecimiento)",
    "create index on {{ this }} (sk_colonia)",
    "create index on {{ this }} (sk_tramo)",
    "create index on {{ this }} (sk_conglomerado)",
    "create index on {{ this }} using gist (geom)"
]) }}

-- Grano: un establecimiento por edición del DENUE.
-- x_m, y_m: metros en UTM 14N con origen en el Zócalo (19.4326, -99.1332).
with origen as (
    select st_transform(st_setsrid(st_makepoint(-99.1332, 19.4326), 4326), 32614) as p
)

select
    d.ordinal                                       as sk_edicion,
    u.sk_ubicacion,
    a.sk_actividad,
    s.sk_estrato,
    de.sk_establecimiento,
    ac.sk_colonia,
    coalesce(cg.sk_conglomerado, 0)                 as sk_conglomerado,
    atr.sk_tramo,
    d.id_denue,
    1                                               as cantidad,
    d.longitud,
    d.latitud,
    d.geom::geography(point, 4326)                  as geom,
    (st_x(d.geom_utm) - st_x(o.p))::real            as x_m,
    (st_y(d.geom_utm) - st_y(o.p))::real            as y_m,
    d.sitio_web is not null                         as tiene_web,
    d.correo is not null                            as tiene_correo,
    d.telefono is not null                          as tiene_telefono,
    ac.metodo_colonia,
    ac.metodo_colonia = 'cercania'                  as colonia_por_cercania,
    ac.alcaldia_colonia,
    ac.distancia_alcaldia_declarada_m,
    atr.metodo_tramo,
    d.texto_danado
from {{ ref('denue_valido') }} d
cross join origen o
join {{ ref('entidad_establecimiento') }} e on e.edicion = d.edicion and e.id_denue = d.id_denue
join {{ ref('dim_establecimiento') }} de
  on de.sk_entidad = e.sk_entidad and d.ordinal between de.desde_ordinal and de.hasta_ordinal
join {{ ref('dim_ubicacion') }} u
  on u.clave_ubicacion = {{ clave_ubicacion('d.cve_manzana', 'd.codigo_postal', 'd.tipo_asentamiento', 'd.colonia') }}
join {{ ref('dim_actividad') }} a on a.version_scian = d.version_scian and a.clase_scian = d.clase_scian
join {{ ref('dim_estrato') }} s on s.estrato = d.estrato
join {{ ref('asignacion_colonia') }} ac on ac.edicion = d.edicion and ac.id_denue = d.id_denue
join {{ ref('asignacion_tramo') }} atr on atr.edicion = d.edicion and atr.id_denue = d.id_denue
left join {{ ref('puente_establecimiento_conglomerado') }} cg
  on cg.edicion = d.edicion and cg.id_denue = d.id_denue and cg.es_principal

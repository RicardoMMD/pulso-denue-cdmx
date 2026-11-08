{{ config(post_hook=["create index on {{ this }} (sk_entidad, desde_ordinal, hasta_ordinal)"]) }}

-- SCD tipo 2. Una fila por versión de un establecimiento: cambia la versión cuando cambia alguno de los
-- atributos seguidos (id DENUE, nombre, razón social, tipo, contacto, edificio, piso, fecha de alta)
-- o cuando el establecimiento no estuvo en la edición inmediata anterior.
-- clee no se sigue: cambia con cada reclasificación; se conserva el valor de la primera edición de la versión.

with base as (
    select
        e.sk_entidad, d.ordinal, d.edicion, d.id_denue, d.clee, d.nombre, d.razon_social, d.tipo_unidad,
        d.telefono, d.correo, d.sitio_web, d.edificio, d.piso, d.fecha_alta,
        md5(concat_ws('|', d.id_denue::text, coalesce(d.nombre, ''), coalesce(d.razon_social, ''),
            coalesce(d.tipo_unidad, ''), coalesce(d.telefono, ''), coalesce(d.correo, ''),
            coalesce(d.sitio_web, ''), coalesce(d.edificio, ''), coalesce(d.piso, ''),
            coalesce(d.fecha_alta::text, ''))) as huella
    from {{ ref('denue_valido') }} d
    join {{ ref('entidad_establecimiento') }} e using (edicion, id_denue)
),

marcado as (
    select *,
        case when lag(huella) over w is distinct from huella or lag(ordinal) over w is distinct from ordinal - 1
             then 1 else 0 end as inicia
    from base
    window w as (partition by sk_entidad order by ordinal)
),

versionado as (
    select *, sum(inicia) over (partition by sk_entidad order by ordinal) as n_version from marcado
),

versiones as (
    select distinct on (sk_entidad, n_version)
        sk_entidad, n_version,
        min(ordinal) over (partition by sk_entidad, n_version) as desde_ordinal,
        max(ordinal) over (partition by sk_entidad, n_version) as hasta_ordinal,
        min(ordinal) over (partition by sk_entidad)            as alta_ordinal,
        max(ordinal) over (partition by sk_entidad)            as ultima_ordinal,
        id_denue, clee, nombre, razon_social, tipo_unidad, telefono, correo, sitio_web, edificio, piso, fecha_alta
    from versionado
    order by sk_entidad, n_version, ordinal
),

ultima as (select max(sk_edicion) as max_ordinal from {{ ref('dim_edicion') }})

select
    row_number() over (order by v.sk_entidad, v.n_version)::int as sk_establecimiento,
    v.sk_entidad,
    v.id_denue, v.clee, v.nombre, v.razon_social, v.tipo_unidad,
    v.telefono, v.correo, v.sitio_web, v.edificio, v.piso, v.fecha_alta,
    v.desde_ordinal, v.hasta_ordinal,
    ed.edicion as vigente_desde,
    eh.edicion as vigente_hasta,
    ea.edicion as edicion_alta,
    case when v.ultima_ordinal < u.max_ordinal then eb.edicion end as edicion_baja,
    (v.hasta_ordinal = u.max_ordinal) as es_vigente
from versiones v
cross join ultima u
join {{ ref('dim_edicion') }} ed on ed.sk_edicion = v.desde_ordinal
join {{ ref('dim_edicion') }} eh on eh.sk_edicion = v.hasta_ordinal
join {{ ref('dim_edicion') }} ea on ea.sk_edicion = v.alta_ordinal
left join {{ ref('dim_edicion') }} eb on eb.sk_edicion = v.ultima_ordinal + 1

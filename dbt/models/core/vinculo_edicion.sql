{{ config(post_hook=[
    "create index on {{ this }} (edicion_previa, id_previo)",
    "create unique index on {{ this }} (edicion, id_denue)"
]) }}

-- Reconciliación entre ediciones. Una fila por establecimiento y edición.
--   id        mismo id DENUE en la edición inmediata anterior
--   difuso    id distinto: mismo nombre normalizado + misma clase SCIAN (o su equivalente entre SCIAN 2018 y 2023)
--             + menos de 30 m, contra la edición inmediata anterior (uno a uno, el más cercano)
--   id_salto  mismo id DENUE en una edición anterior no inmediata: faltó en una o más ediciones y volvió.
--             Se vincula a su última aparición, siempre que ese registro no tenga ya sucesor.
--   id_reusado  mismo id que un registro anterior, pero es otro negocio: INEGI reasignó el id. Se trata como alta
--             nueva (raíz de una entidad). Regla: nombres sin parecido (word_similarity < 0.4 en ambos sentidos),
--             rama distinta (sin equivalencia SCIAN 2018→2023) y a más de 100 m.
--   ninguno   alta nueva (o primera edición de la serie)
-- edicion_previa es la edición del registro vinculado (la inmediata anterior, salvo en id_salto).
-- Los registros sin sucesor quedan como baja (ver dim_establecimiento).

with ediciones as (
    select edicion, sk_edicion, version_scian, lag(edicion) over (order by sk_edicion) as edicion_previa
    from {{ ref('dim_edicion') }}
),

v as (
    select d.edicion, d.ordinal, d.id_denue, d.clase_scian, d.version_scian, d.nombre_norm, d.geom_utm, e.edicion_previa
    from {{ ref('denue_valido') }} d
    join ediciones e using (edicion)
),

-- clase 2018 → clases 2023 equivalentes (incluye las que conservan código)
equivalencia as (
    select clase_2018, clase_2023 from {{ ref('scian_correspondencia') }}
),

mismo_id as (
    select a.edicion, a.id_denue, a.edicion_previa, b.id_denue as id_previo,
           st_distance(a.geom_utm, b.geom_utm) as distancia_m,
           {{ es_reuso('a', 'b') }} as reuso
    from v a
    join v b on b.edicion = a.edicion_previa and b.id_denue = a.id_denue
),

por_id as (
    select edicion, id_denue, edicion_previa, id_previo, 'id'::text as metodo, distancia_m
    from mismo_id
    where not reuso
),

nuevos as (
    select a.* from v a
    where a.edicion_previa is not null and a.nombre_norm is not null
      and not exists (select 1 from por_id p where p.edicion = a.edicion and p.id_denue = a.id_denue)
),

viejos as (
    select b.* from v b
    where b.nombre_norm is not null
      and exists (select 1 from ediciones s where s.edicion_previa = b.edicion)
      and not exists (select 1 from por_id p where p.edicion_previa = b.edicion and p.id_previo = b.id_denue)
),

candidatos as (
    select n.edicion, n.id_denue, n.edicion_previa, o.id_denue as id_previo,
           st_distance(n.geom_utm, o.geom_utm) as distancia_m
    from nuevos n
    join viejos o
      on o.edicion = n.edicion_previa
     and o.nombre_norm = n.nombre_norm
     and st_dwithin(n.geom_utm, o.geom_utm, 30)
    where o.clase_scian = n.clase_scian
       or (o.version_scian = 'SCIAN 2018' and n.version_scian = 'SCIAN 2023'
           and exists (select 1 from equivalencia q where q.clase_2018 = o.clase_scian and q.clase_2023 = n.clase_scian))
),

mejor_por_nuevo as (
    select *, row_number() over (partition by edicion, id_denue order by distancia_m, id_previo) as rn
    from candidatos
),

difuso as (
    select edicion, id_denue, edicion_previa, id_previo, 'difuso'::text as metodo, distancia_m
    from (
        select *, row_number() over (partition by edicion_previa, id_previo order by distancia_m, id_denue) as rn2
        from mejor_por_nuevo where rn = 1
    ) x
    where rn2 = 1
),

inmediatos as (
    select * from por_id
    union all
    select * from difuso
),

-- Sin pareja en la edición inmediata anterior: ¿el mismo id aparece antes? Se toma su última aparición.
sin_pareja as (
    select a.* from v a
    where a.edicion_previa is not null
      and not exists (select 1 from inmediatos p where p.edicion = a.edicion and p.id_denue = a.id_denue)
),

ultima_aparicion as (
    select distinct on (s.edicion, s.id_denue)
        s.edicion, s.id_denue, b.edicion as edicion_previa, b.id_denue as id_previo,
        st_distance(s.geom_utm, b.geom_utm) as distancia_m,
        {{ es_reuso('s', 'b') }} as reuso
    from sin_pareja s
    join v b on b.id_denue = s.id_denue and b.ordinal < s.ordinal - 1
    order by s.edicion, s.id_denue, b.ordinal desc
),

salto as (
    select edicion, id_denue, edicion_previa, id_previo, 'id_salto'::text as metodo, distancia_m
    from ultima_aparicion u
    -- la última aparición no debe tener ya sucesor (difuso en la edición siguiente) ni ser otro negocio
    where not u.reuso and not exists (select 1 from inmediatos p where p.edicion_previa = u.edicion_previa and p.id_previo = u.id_previo)
),

pareados as (
    select * from inmediatos
    union all
    select * from salto
),

reusados as (
    select edicion, id_denue from mismo_id where reuso
    union
    select edicion, id_denue from ultima_aparicion where reuso
)

select * from pareados
union all
select v.edicion, v.id_denue, v.edicion_previa, null::bigint,
       case when r.id_denue is not null then 'id_reusado' else 'ninguno' end, null::double precision
from v
left join reusados r using (edicion, id_denue)
where not exists (select 1 from pareados p where p.edicion = v.edicion and p.id_denue = v.id_denue)

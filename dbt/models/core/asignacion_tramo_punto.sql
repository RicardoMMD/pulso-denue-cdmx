{{ config(post_hook=["create index on {{ this }} (vialidad_norm, x, y)"]) }}

-- Tramo de calle de cada combinación única de (vialidad del DENUE, ubicación). Se calcula sobre ubicaciones
-- distintas, no sobre los 1.86 millones de filas, porque un establecimiento conserva su punto entre ediciones.
--   nombre           el tramo más cercano (≤ 60 m) cuyo nombre normalizado es igual al de la vialidad del DENUE
--   nombre_similar   idem con similitud de trigramas ≥ 0.55 y los mismos números (26 de enero ≠ 25 de enero)
--   cercania         ningún nombre coincide: el tramo más cercano a ≤ 30 m
--   ninguno          sk_tramo = 0
with claves as (
    select distinct
        {{ vialidad_denue_norm('vialidad') }}                                as vialidad_norm,
        round(st_x(geom_utm)::numeric, 2)                                     as x,
        round(st_y(geom_utm)::numeric, 2)                                     as y
    from {{ ref('denue_valido') }}
),

candidatos as (
    select
        k.vialidad_norm, k.x, k.y, t.sk_tramo, t.nombre_norm,
        st_distance(t.geom_utm, p.pt) as distancia_m
    from claves k
    cross join lateral (select st_setsrid(st_makepoint(k.x, k.y), 32614) as pt) p
    cross join lateral (
        select sk_tramo, nombre_norm, geom_utm
        from {{ ref('dim_tramo') }} t
        where t.sk_tramo > 0
        order by t.geom_utm <-> p.pt
        limit 15
    ) t
),

clasificados as (
    select *,
        case
            when vialidad_norm is not null and nombre_norm = vialidad_norm and distancia_m <= 60 then 1
            when vialidad_norm is not null and nombre_norm is not null
                 and similarity(nombre_norm, vialidad_norm) >= 0.55 and distancia_m <= 60
                 and regexp_replace(nombre_norm, '[^0-9]', '', 'g') = regexp_replace(vialidad_norm, '[^0-9]', '', 'g') then 2
            when distancia_m <= 30 then 3
        end as prioridad
    from candidatos
),

mejor as (
    select distinct on (vialidad_norm, x, y)
        vialidad_norm, x, y, sk_tramo, distancia_m,
        case prioridad when 1 then 'nombre' when 2 then 'nombre_similar' else 'cercania' end as metodo_tramo
    from clasificados
    where prioridad is not null
    order by vialidad_norm, x, y, prioridad, distancia_m
)

select c.vialidad_norm, c.x, c.y,
       coalesce(m.sk_tramo, 0)                       as sk_tramo,
       coalesce(m.metodo_tramo, 'ninguno')           as metodo_tramo,
       m.distancia_m
from claves c
left join mejor m on m.x = c.x and m.y = c.y and m.vialidad_norm is not distinct from c.vialidad_norm

{{ config(post_hook=["create unique index on {{ this }} (edicion, id_denue)"]) }}

-- Colonia de cada establecimiento por edición:
--   poligono  el punto cae dentro de un polígono (si cae en dos, el de menor área)
--   cercania  fuera de todo polígono, colonia más cercana a menos de 50 m
--   nombre    fuera de todo polígono y lejos: la colonia que declara el DENUE se parece (trigramas ≥ 0.5) a una
--             del catálogo de la misma alcaldía que está a menos de 2 km; gana la más parecida, luego la más cercana
--   ninguna   sin colonia: miembro "sin colonia (<alcaldía>)" (sk_colonia = -cve_municipio), o 0 si no hay alcaldía
--
-- Coherencia con la alcaldía que declara el DENUE (solo para colonias reales):
--   alcaldia_colonia     coincide | frontera (la colonia es de otra alcaldía, pero el punto está a ≤ 100 m de la
--                        alcaldía declarada: ruido de límite) | discrepante (a más de 100 m)
--   distancia_alcaldia_declarada_m  distancia del punto al límite oficial de la alcaldía declarada (dim_alcaldia, Marco Geoestadístico 2020)
with puntos as (
    select edicion, id_denue, cve_municipio, geom_utm,
           nullif(upper(regexp_replace(unaccent(colonia), '\s+', ' ', 'g')), '') as colonia_norm
    from {{ ref('denue_valido') }}
),

colonias as (
    select sk_colonia, cve_municipio, area_m2, geom_utm,
           upper(regexp_replace(unaccent(colonia), '\s+', ' ', 'g')) as colonia_norm
    from {{ ref('dim_colonia') }}
    where not es_especial
),

dentro as (
    select distinct on (d.edicion, d.id_denue)
        d.edicion, d.id_denue, c.sk_colonia, 'poligono'::text as metodo_colonia, 0::double precision as distancia_m
    from puntos d
    join colonias c on st_covers(c.geom_utm, d.geom_utm)
    order by d.edicion, d.id_denue, c.area_m2
),

fuera as (
    select d.*
    from puntos d
    where not exists (select 1 from dentro x where x.edicion = d.edicion and x.id_denue = d.id_denue)
),

cerca as (
    select f.edicion, f.id_denue, c.sk_colonia, 'cercania'::text, st_distance(c.geom_utm, f.geom_utm)
    from fuera f
    cross join lateral (
        select sk_colonia, geom_utm from colonias c
        where st_dwithin(c.geom_utm, f.geom_utm, 50)
        order by c.geom_utm <-> f.geom_utm
        limit 1
    ) c
),

lejos as (
    select f.* from fuera f
    where not exists (select 1 from cerca x where x.edicion = f.edicion and x.id_denue = f.id_denue)
),

por_nombre as (
    select f.edicion, f.id_denue, c.sk_colonia, 'nombre'::text, st_distance(c.geom_utm, f.geom_utm)
    from lejos f
    cross join lateral (
        select sk_colonia, geom_utm from colonias c
        where c.cve_municipio = f.cve_municipio
          and f.colonia_norm is not null
          and similarity(c.colonia_norm, f.colonia_norm) >= 0.5
          and st_dwithin(c.geom_utm, f.geom_utm, 2000)
        order by similarity(c.colonia_norm, f.colonia_norm) desc, c.geom_utm <-> f.geom_utm
        limit 1
    ) c
),

sin_colonia as (
    select f.edicion, f.id_denue, coalesce(e.sk_colonia, 0), 'ninguna'::text, null::double precision
    from lejos f
    left join {{ ref('dim_colonia') }} e on e.es_especial and e.sk_colonia = -(f.cve_municipio::int)
    where not exists (select 1 from por_nombre x where x.edicion = f.edicion and x.id_denue = f.id_denue)
),

asignado as (
    select * from dentro
    union all select * from cerca
    union all select * from por_nombre
    union all select * from sin_colonia
)

select
    a.edicion, a.id_denue, a.sk_colonia, a.metodo_colonia, a.distancia_m,
    case
        when c.es_especial then null
        when c.cve_municipio = p.cve_municipio then 'coincide'
        when st_distance(p.geom_utm, al.geom_utm) <= 100 then 'frontera'
        else 'discrepante'
    end                                                                   as alcaldia_colonia,
    case when not c.es_especial and c.cve_municipio <> p.cve_municipio
         then round(st_distance(p.geom_utm, al.geom_utm)::numeric, 1) end as distancia_alcaldia_declarada_m
from asignado a
join puntos p using (edicion, id_denue)
join {{ ref('dim_colonia') }} c on c.sk_colonia = a.sk_colonia
left join {{ ref('dim_alcaldia') }} al on al.cve_municipio = p.cve_municipio

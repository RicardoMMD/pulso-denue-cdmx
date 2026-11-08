{{ config(post_hook=[
    "create index on {{ this }} using gist (geom_utm)",
    "create index on {{ this }} (edicion, id_denue)"
]) }}

-- Establecimientos que entran al modelo: staging sin los puntos fuera de CDMX.
-- Agrega el orden de la edición, la geometría proyectada (UTM 14N, metros) y el nombre normalizado
-- que usa la reconciliación difusa.
select
    e.sk_edicion                                                     as ordinal,
    e.version_scian,
    s.*,
    st_transform(s.geom, 32614)::geometry(point, 32614)              as geom_utm,
    nullif(upper(regexp_replace(unaccent(trim(s.nombre)), '\s+', ' ', 'g')), '') as nombre_norm
from {{ ref('stg_denue') }} s
join {{ ref('dim_edicion') }} e using (edicion)
where s.coord_en_cdmx

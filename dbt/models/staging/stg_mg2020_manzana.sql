{{ config(post_hook=["create index on {{ this }} (cve_manzana)"]) }}

-- Manzanas del Marco Geoestadístico 2020 (claves de 16 caracteres, iguales a cve_manzana del DENUE y del Censo 2020).
-- punto: un punto interior de la manzana, en UTM 14N, para asignarla a colonia.
select
    cvegeo                                                                as cve_manzana,
    cve_mun                                                               as cve_municipio,
    cve_ent || cve_mun || cve_loc || cve_ageb                             as cve_ageb,
    ambito,
    tipomza                                                               as tipo_manzana,
    st_area(st_transform(geom, 32614))                                    as area_m2,
    st_pointonsurface(st_transform(geom, 32614))::geometry(point, 32614)  as punto_utm
from {{ source('raw', 'mg2020_manzana') }}

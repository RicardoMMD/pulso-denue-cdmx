-- Polígonos de colonia válidos, en grados y en UTM 14N.
select
    cve_col,
    trim(colonia)                                                    as colonia,
    clasif                                                           as clasificacion,
    cve_ent || cve_alc                                               as cve_mun_completa,
    cve_alc                                                          as cve_municipio,
    trim(alcaldia)                                                   as alcaldia,
    st_multi(st_collectionextract(st_makevalid(geom), 3))::geometry(multipolygon, 4326) as geom,
    st_transform(st_multi(st_collectionextract(st_makevalid(geom), 3)), 32614)::geometry(multipolygon, 32614) as geom_utm
from {{ source('raw', 'colonias_cdmx') }}

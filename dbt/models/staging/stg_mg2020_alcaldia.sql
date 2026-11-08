-- Límites oficiales de alcaldía del Marco Geoestadístico 2020 de INEGI, en UTM 14N.
select
    cve_mun                                                               as cve_municipio,
    trim(nomgeo)                                                          as nombre,
    st_multi(st_collectionextract(st_makevalid(st_transform(geom, 32614)), 3))::geometry(multipolygon, 32614) as geom_utm
from {{ source('raw', 'mg2020_municipio') }}

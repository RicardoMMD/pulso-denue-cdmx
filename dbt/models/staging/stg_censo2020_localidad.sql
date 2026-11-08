-- Censo 2020 por localidad (ITER), CDMX. Una fila por localidad; excluye totales de entidad y de alcaldía
-- (loc 0000) y las agrupaciones de localidades de una y dos viviendas (9998, 9999), que no tienen ubicación.
-- Las coordenadas vienen en grados, minutos y segundos ("99°11'03.698" W") y se pasan a grados decimales.
with fuente as (
    select *,
        regexp_match(longitud, '(\d+)°(\d+)''([\d.]+)" ([EW])') as lon_dms,
        regexp_match(latitud, '(\d+)°(\d+)''([\d.]+)" ([NS])')  as lat_dms
    from {{ source('raw', 'censo2020_iter') }}
    where mun <> '000' and loc not in ('0000', '9998', '9999')
)

select
    entidad || mun || loc                                                  as cve_localidad,
    mun                                                                    as cve_municipio,
    loc,
    trim(nom_loc)                                                          as nombre,
    case when pobtot ~ '^\d+$' then pobtot::int end                        as poblacion,
    tamloc                                                                 as tamano_localidad,
    st_transform(st_setsrid(st_makepoint(
        (case lon_dms[4] when 'W' then -1 else 1 end) * (lon_dms[1]::numeric + lon_dms[2]::numeric / 60 + lon_dms[3]::numeric / 3600),
        (case lat_dms[4] when 'S' then -1 else 1 end) * (lat_dms[1]::numeric + lat_dms[2]::numeric / 60 + lat_dms[3]::numeric / 3600)
    ), 4326), 32614)::geometry(point, 32614)                               as punto_utm
from fuente

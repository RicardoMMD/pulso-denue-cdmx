-- Mercados públicos con tipos numéricos y geometría.
select
    row_number() over (order by trim(alcaldia), trim(mercado))::int as id_mercado,
    trim(mercado)                              as mercado,
    trim(alcaldia)                             as alcaldia,
    trim(colonia)                              as colonia,
    trim(direccion)                            as direccion,
    tipo,
    nullif(num_locales, '')::numeric::int      as num_locales,
    nullif(superficie_m2, '')::numeric         as superficie_m2,
    nullif(inauguracion, '')::numeric::int     as anio_inauguracion,
    protegido = 'SI'                           as protegido,
    geom::geometry(point, 4326)                as geom,
    st_transform(geom, 32614)::geometry(point, 32614) as geom_utm
from {{ source('raw', 'mercados_publicos') }}

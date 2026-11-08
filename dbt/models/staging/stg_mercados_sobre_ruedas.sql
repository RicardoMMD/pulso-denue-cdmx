select
    row_number() over (order by ruta, nullif(punto, '')::numeric)::int as id_msr,
    trim(ruta)                                      as ruta,
    trim(dia)                                       as dia,
    trim(direccion)                                 as direccion,
    trim(alcaldia)                                  as alcaldia,
    trim(colonia)                                   as colonia,
    nullif(num_oferentes, '')::numeric::int         as num_oferentes,
    geom::geometry(point, 4326)                     as geom,
    st_transform(geom, 32614)::geometry(point, 32614) as geom_utm
from {{ source('raw', 'mercados_sobre_ruedas') }}

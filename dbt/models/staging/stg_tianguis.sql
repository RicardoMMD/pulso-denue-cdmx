select
    row_number() over (order by trim(alcaldia), trim(colonia), trim(ubicacion), dia)::int as id_tianguis,
    trim(alcaldia)                                  as alcaldia,
    trim(colonia)                                   as colonia,
    nullif(nullif(trim(giro), 'None'), '0')         as giro,
    trim(dia)                                       as dia,
    trim(horario)                                   as horario,
    trim(ubicacion)                                 as ubicacion,
    nullif(num_oferentes, '')::numeric::int         as num_oferentes,
    geom::geometry(point, 4326)                     as geom,
    st_transform(geom, 32614)::geometry(point, 32614) as geom_utm
from {{ source('raw', 'tianguis') }}

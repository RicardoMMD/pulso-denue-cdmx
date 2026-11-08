-- Diccionario de las variables económicas de los Censos Económicos 2024.
-- La unidad se toma del texto de la descripción; 'conteo' para personal y unidades.
-- Las columnas de clave (E03, E04, SECTOR... ID_ESTRATO) quedan con unidad nula.
select
    row_number() over (order by variable)::int as sk_variable,
    variable,
    descripcion,
    case
        when descripcion ilike '%millones de pesos%' then 'millones de pesos'
        when descripcion ilike '%miles de horas%' then 'miles de horas'
        -- UE y personal (H dependiente, I no dependiente; A total, B hombres, C mujeres)
        when variable ~ '^(UE|[HI]\d+[ABC])$' then 'conteo'
        else null
    end                                        as unidad,
    tipo_dato,
    rango_valido
from {{ ref('stg_ce_variable') }}

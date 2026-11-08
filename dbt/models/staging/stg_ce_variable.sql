select
    upper(trim(columna))                             as variable,
    trim(descripcion)                                as descripcion,
    lower(trim(tipo_dato))                           as tipo_dato,
    nullif(trim(longitud), '')                       as longitud,
    nullif(trim(codigo_valido), '')                  as rango_valido
from {{ source('raw', 'ce2024_diccionario') }}

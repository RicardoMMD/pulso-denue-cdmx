-- Catálogo SCIAN 2023 de los Censos Económicos 2024: un código por nivel, con su nombre.
select
    trim(codigo)                                     as codigo,
    trim(desc_codigo)                                as nombre,
    lower(trim(clasificador_codigo))                 as nivel
from {{ source('raw', 'ce2024_catalogo_actividad') }}
where codigo is not null

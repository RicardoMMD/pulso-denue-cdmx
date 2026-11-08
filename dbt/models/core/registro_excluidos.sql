-- Qué se dejó fuera del modelo y por qué. Decisión: los puntos con coordenadas fuera de CDMX se excluyen.
select
    edicion,
    id_denue,
    clee,
    nombre,
    latitud,
    longitud,
    'coordenada fuera de CDMX' as motivo
from {{ ref('stg_denue') }}
where not coord_en_cdmx

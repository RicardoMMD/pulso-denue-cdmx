-- Correspondencia de clases SCIAN 2018 (las ediciones del DENUE en SCIAN 2018, hoy solo 05/2024) a SCIAN 2023.
-- Fuente: INEGI, Tabla comparativa I SCIAN México 2023-SCIAN México 2018 (tablaxv.pdf), que solo lista
-- las clases que cambian. Las clases 2018 que no aparecen ahí conservan código en 2023 (tipo 'igual').
-- 'parte' = a/b cuando la clase 2018 se reparte en b clases 2023.
with tabla as (
    select clase_2018, clase_2023, nullif(parte, '') as parte from {{ ref('ref_scian_2023_2018') }}
)

select
    a.clase_scian                               as clase_2018,
    coalesce(t.clase_2023, a.clase_scian)       as clase_2023,
    t.parte,
    case
        when t.clase_2018 is null then 'igual'
        when t.parte is not null then 'parcial'
        when t.clase_2023 = a.clase_scian then 'mismo codigo, cambia nombre o contenido'
        else 'cambia codigo'
    end                                         as tipo
from {{ ref('dim_actividad') }} a
left join tabla t on t.clase_2018 = a.clase_scian
where a.version_scian = 'SCIAN 2018'

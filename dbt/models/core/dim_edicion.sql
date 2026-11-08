-- Una fila por edición del DENUE cargada. sk_edicion sigue el orden cronológico.
-- version_scian se deduce de los datos, no del diccionario: INEGI dice "SCIAN 2018" en el diccionario
-- de todas las ediciones, pero desde 11/2024 los códigos ya son SCIAN 2023. Una edición es SCIAN 2023
-- si trae clases que solo existen en 2023 (tabla comparativa de INEGI) y ninguna que solo exista en 2018.
-- Si trae de ambas, sale 'mixta' y la prueba de valores aceptados falla.
-- comparable_con_anterior: falso cuando la edición cambió de fuente respecto de la anterior, es decir, cambió la
-- versión SCIAN o más del 10 % de sus ids no estaban en la edición anterior (11/2024: 29 %, incorporación del
-- Censo Económico 2024; las demás, 2-3 %). Las series que crucen una edición no comparable mezclan
-- crecimiento real con cambio de fuente. Nulo en la primera edición.
with tabla as (
    select clase_2018, clase_2023 from {{ ref('ref_scian_2023_2018') }}
),

solo_2023 as (
    select clase_2023 as clase from tabla
    except
    select clase_2018 from tabla
),

solo_2018 as (
    select clase_2018 as clase from tabla
    except
    select clase_2023 from tabla
),

clases as (
    select distinct edicion, clase_scian from {{ ref('stg_denue') }}
),

ids as (
    select distinct edicion, id_denue from {{ ref('stg_denue') }}
),

ids_nuevos as (
    -- proporción de ids de la edición que no estaban en la edición anterior
    select a.edicion,
           avg(case when b.id_denue is null then 1.0 else 0.0 end) as proporcion_ids_nuevos
    from ids a
    join (select edicion, lag(edicion) over (order by edicion) as previa from {{ source('raw', 'carga_log') }}) e
      on e.edicion = a.edicion and e.previa is not null
    left join ids b on b.edicion = e.previa and b.id_denue = a.id_denue
    group by 1
),

deteccion as (
    select
        c.edicion,
        count(*) filter (where c.clase_scian in (select clase from solo_2023)) as clases_solo_2023,
        count(*) filter (where c.clase_scian in (select clase from solo_2018)) as clases_solo_2018
    from clases c
    group by 1
),

version as (
    select edicion,
        case
            when clases_solo_2023 > 0 and clases_solo_2018 = 0 then 'SCIAN 2023'
            when clases_solo_2018 > 0 and clases_solo_2023 = 0 then 'SCIAN 2018'
            else 'mixta'
        end as version_scian
    from deteccion
)

select
    row_number() over (order by l.edicion)::int as sk_edicion,
    l.edicion,
    left(l.edicion, 4)::int                     as anio,
    right(l.edicion, 2)::int                    as mes,
    l.publicacion                               as fecha_corte,
    v.version_scian,
    round(n.proporcion_ids_nuevos, 4)           as proporcion_ids_nuevos,
    case
        when n.edicion is null then null
        else n.proporcion_ids_nuevos <= 0.10
             and v.version_scian = lag(v.version_scian) over (order by l.edicion)
    end                                         as comparable_con_anterior,
    l.cargado_en                                as fecha_carga,
    l.filas                                     as filas_origen
from {{ source('raw', 'carga_log') }} l
left join version v using (edicion)
left join ids_nuevos n using (edicion)

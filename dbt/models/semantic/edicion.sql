-- Ediciones del DENUE disponibles. Toda respuesta cita la fecha de corte de su edición.
select
    e.edicion,
    e.fecha_corte,
    e.version_scian,
    e.sk_edicion = max(e.sk_edicion) over ()          as es_vigente,
    e.comparable_con_anterior,
    e.proporcion_ids_nuevos,
    count(f.*)                                         as establecimientos
from {{ ref('dim_edicion') }} e
left join {{ ref('fact_establecimiento') }} f on f.sk_edicion = e.sk_edicion
group by e.sk_edicion, e.edicion, e.fecha_corte, e.version_scian, e.comparable_con_anterior, e.proporcion_ids_nuevos

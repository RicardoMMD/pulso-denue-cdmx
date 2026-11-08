-- Falla si un id DENUE aparece más de una vez en la misma edición del hecho (uniones que duplican filas).
select sk_edicion, id_denue, count(*) as filas
from {{ ref('fact_establecimiento') }}
group by 1, 2
having count(*) > 1

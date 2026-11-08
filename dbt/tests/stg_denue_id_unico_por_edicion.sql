-- Falla si un establecimiento aparece más de una vez en la misma edición.
select edicion, id_denue, count(*) as veces
from {{ ref('stg_denue') }}
group by 1, 2
having count(*) > 1

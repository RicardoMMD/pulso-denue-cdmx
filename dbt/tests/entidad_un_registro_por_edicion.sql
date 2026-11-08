-- Falla si una entidad de establecimiento tiene más de un registro en la misma edición
-- (la reconciliación entre ediciones debe ser uno a uno).
select edicion, sk_entidad, count(*) as registros
from {{ ref('entidad_establecimiento') }}
group by 1, 2
having count(*) > 1

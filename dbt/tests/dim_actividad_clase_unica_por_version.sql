-- Falla si una clase SCIAN se repite dentro de la misma versión de dim_actividad.
select version_scian, clase_scian, count(*) as filas
from {{ ref('dim_actividad') }}
group by 1, 2
having count(*) > 1

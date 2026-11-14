-- Las estaciones fuera de la Ciudad no entran al ranking, y las de la Ciudad sí.
-- La red tiene 11 estaciones en el Estado de México (Línea B de Múzquiz a Ciudad Azteca, La Paz, Los Reyes y
-- Cuatro Caminos). Falla si cambia ese número: o el límite de alcaldías o la ubicación en OpenStreetMap se movió.
select 'lugar_incoherente' as problema, estacion_norm as detalle
from {{ ref('metro_estacion') }}
where (lugar is null) = en_cdmx
union all
select 'estaciones_fuera', count(*)::text
from {{ ref('dim_estacion_metro') }}
where not en_cdmx
having count(*) <> 11

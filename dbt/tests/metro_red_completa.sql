-- La red del Metro (STC) tiene 12 líneas y 195 pares línea-estación. Falla si OpenStreetMap trae menos,
-- por ejemplo si una relación de línea perdió paradas.
select count(distinct cve_linea) as lineas, count(*) as pares
from {{ ref('stg_metro') }}
having count(distinct cve_linea) <> 12 or count(*) <> 195

-- Macrosectores del portal: agrupación de los sectores SCIAN en 7 familias para leer la ciudad de un vistazo.
-- La agrupación vive en las semillas ref_macrosector y ref_scian_sector (columna cve_macrosector); cambiarla
-- no requiere tocar el modelo. El color de cada macrosector se define en el sistema visual, no aquí.
select
    row_number() over (order by orden)::int as sk_macrosector,
    cve_macrosector, nombre_macrosector, orden
from {{ ref('ref_macrosector') }}

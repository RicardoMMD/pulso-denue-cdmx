select
    row_number() over (order by s.cve_sector)::int as sk_sector,
    s.cve_sector, s.nombre_sector, s.sector_agrupado,
    m.sk_macrosector, m.cve_macrosector, m.nombre_macrosector
from {{ ref('ref_scian_sector') }} s
join {{ ref('dim_macrosector') }} m using (cve_macrosector)

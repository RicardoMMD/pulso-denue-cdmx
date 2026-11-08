select
    row_number() over (order by orden)::int as sk_estrato,
    estrato, orden, limite_inferior, limite_superior, punto_medio,
    id_estrato_ce   -- estrato equivalente de los Censos Económicos (0-10, 11-50, 51-250, 251+)
from {{ ref('ref_estrato') }}

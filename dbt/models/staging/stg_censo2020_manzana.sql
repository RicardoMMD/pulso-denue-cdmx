-- Censo de Población y Vivienda 2020 por manzana urbana de CDMX. Solo filas de manzana (no los totales).
-- '*' (confidencial) y 'N/D' (no disponible) pasan a nulo. La población total nunca es confidencial.
{% set variables = {
    'pobtot': 'poblacion', 'pobfem': 'poblacion_mujeres', 'pobmas': 'poblacion_hombres',
    'pob0_14': 'poblacion_0_14', 'pob15_64': 'poblacion_15_64', 'pob65_mas': 'poblacion_65_mas',
    'pea': 'poblacion_economicamente_activa', 'pocupada': 'poblacion_ocupada',
    'tothog': 'hogares', 'tvivparhab': 'viviendas_habitadas', 'vph_inter': 'viviendas_con_internet'
} %}
select
    entidad || mun || loc || ageb || mza                                  as cve_manzana,
    entidad || mun || loc || ageb                                         as cve_ageb,
    mun                                                                   as cve_municipio,
    {% for col, nombre in variables.items() %}
    case when {{ col }} ~ '^\d+$' then {{ col }}::int end                 as {{ nombre }},
    {% endfor %}
    case when graproes ~ '^[\d.]+$' then graproes::numeric end            as escolaridad_promedio
from {{ source('raw', 'censo2020_ageb_mza') }}
where mza <> '000'

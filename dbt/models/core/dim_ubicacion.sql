-- Manzana + código postal + asentamiento. La colonia de DENUE se conserva tal cual; la colonia del
-- catálogo CDMX se asigna por punto (asignacion_colonia) y va en la tabla de hechos.
select
    row_number() over (order by cve_manzana, codigo_postal, tipo_asentamiento, colonia)::int as sk_ubicacion,
    {{ clave_ubicacion('u.cve_manzana', 'u.codigo_postal', 'u.tipo_asentamiento', 'u.colonia') }} as clave_ubicacion,
    g.sk_ageb, g.sk_alcaldia,
    u.cve_manzana, u.manzana, u.codigo_postal, u.tipo_asentamiento,
    u.colonia                    as colonia_denue
from (
    select distinct cve_entidad, cve_municipio, cve_localidad, ageb, cve_manzana, manzana,
                    codigo_postal, tipo_asentamiento, colonia
    from {{ ref('denue_valido') }}
) u
join {{ ref('dim_ageb') }} g
  on g.cve_municipio = u.cve_municipio and g.cve_localidad = u.cve_localidad and g.ageb = u.ageb

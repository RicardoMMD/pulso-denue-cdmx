-- Localidad y AGEB: cada AGEB pertenece a una localidad de una alcaldía.
select
    row_number() over (order by cve_municipio, cve_localidad, ageb)::int as sk_ageb,
    a.sk_alcaldia, cve_municipio, cve_localidad, localidad as nombre_localidad, ageb,
    cve_entidad || cve_municipio || cve_localidad || ageb as cve_ageb
from (
    select distinct on (cve_municipio, cve_localidad, ageb)
        cve_entidad, cve_municipio, cve_localidad, localidad, ageb
    from {{ ref('denue_valido') }}
    order by cve_municipio, cve_localidad, ageb, ordinal desc
) g
join {{ ref('dim_alcaldia') }} a using (cve_entidad, cve_municipio)

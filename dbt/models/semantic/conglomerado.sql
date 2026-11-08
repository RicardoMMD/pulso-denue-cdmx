{{ config(post_hook=["create index on {{ this }} (edicion, cve_municipio)", "create index on {{ this }} using gin (nombre_norm gin_trgm_ops)"]) }}

-- Mercados, plazas, centrales y demás conglomerados (escena Ciudades dentro de la ciudad).
-- Grano: edición × conglomerado. Cuenta los establecimientos cuyo conglomerado principal es este.
-- La alcaldía es la más frecuente entre sus establecimientos. num_locales es lo que declara la fuente
-- (máximo del DENUE, locales del padrón u oferentes del tianguis), no los establecimientos contados.
with base as (
    select edicion, clave_conglomerado, cve_municipio, alcaldia, cve_macrosector, nombre_macrosector
    from {{ ref('establecimiento') }}
    where clave_conglomerado is not null
),

giro as (
    select edicion, clave_conglomerado, nombre_macrosector, count(*) as n,
           row_number() over (partition by edicion, clave_conglomerado order by count(*) desc, nombre_macrosector) as rn
    from base
    group by 1, 2, 3
)

select
    b.edicion,
    b.clave_conglomerado,
    c.nombre,
    upper(unaccent(c.nombre))                                         as nombre_norm,
    c.tipo,
    c.categoria,
    c.origen,
    mode() within group (order by b.cve_municipio)                     as cve_municipio,
    mode() within group (order by b.alcaldia)                          as alcaldia,
    count(*)                                                           as establecimientos,
    g.nombre_macrosector                                               as macrosector_dominante,
    round(g.n::numeric / count(*), 3)                                  as participacion_macrosector_dominante,
    c.num_locales,
    c.superficie_m2,
    st_y(c.geom_centro)                                                as latitud_centro,
    st_x(c.geom_centro)                                                as longitud_centro
from base b
join {{ ref('dim_conglomerado') }} c on c.clave_natural = b.clave_conglomerado
join giro g on g.edicion = b.edicion and g.clave_conglomerado = b.clave_conglomerado and g.rn = 1
group by b.edicion, b.clave_conglomerado, c.nombre, c.tipo, c.categoria, c.origen, g.nombre_macrosector, g.n,
         c.num_locales, c.superficie_m2, c.geom_centro

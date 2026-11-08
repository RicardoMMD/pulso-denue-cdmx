-- Paridad: todas las tablas de semantic deben sumar lo mismo que el hecho por edición.
-- Falla con una fila por edición y tabla que no cuadra.
with hecho as (
    select e.edicion, count(*) as n
    from {{ ref('fact_establecimiento') }} f join {{ ref('dim_edicion') }} e using (sk_edicion)
    group by 1
),
tablas as (
    select 'establecimiento' as tabla, edicion, count(*) as n from {{ ref('establecimiento') }} group by 2
    union all select 'edicion', edicion, establecimientos from {{ ref('edicion') }}
    union all select 'resumen_territorio (ciudad)', edicion, establecimientos from {{ ref('resumen_territorio') }} where nivel = 'ciudad'
    union all select 'resumen_territorio (alcaldías)', edicion, sum(establecimientos) from {{ ref('resumen_territorio') }} where nivel = 'alcaldia' group by 2
    union all select 'perfil_sector (alcaldías)', edicion, sum(establecimientos) from {{ ref('perfil_sector') }} where nivel = 'alcaldia' group by 2
    union all select 'conteo_clase (ciudad)', edicion, sum(establecimientos) from {{ ref('conteo_clase') }} where nivel = 'ciudad' group by 2
    union all select 'conteo_clase (alcaldías)', edicion, sum(establecimientos) from {{ ref('conteo_clase') }} where nivel = 'alcaldia' group by 2
)
select t.tabla, t.edicion, t.n, h.n as hecho
from tablas t
join hecho h using (edicion)
where t.n <> h.n

{{ config(post_hook=["create index on {{ this }} (edicion, nivel, cve_territorio)", "create index on {{ this }} (edicion, palabra)"]) }}

-- Cómo se llaman las cosas: palabras de los nombres comerciales por territorio.
-- Grano: edición × territorio (ciudad, alcaldía o colonia) × palabra.
-- Se excluyen los nombres genéricos que pone INEGI cuando el negocio no tiene nombre (terminan en SIN NOMBRE),
-- las palabras vacías (artículos, preposiciones, siglas societarias) y las de menos de 3 letras.
-- Frecuencia mínima para evitar ruido: 5 en la ciudad y alcaldías, 3 en colonias.
--   es_diminutivo  termina en -ITO/-ITA/-ITOS/-ITAS/-CITO/-CITA (LA TIENDITA, EL GORDITO)
--   lugar          posición por frecuencia dentro del territorio
-- Pendiente: marcar nombres propios (requiere un catálogo de nombres de pila).
with nombres as (
    select edicion, cve_municipio, alcaldia, cve_col, colonia, nombre
    from {{ ref('establecimiento') }}
    where nombre is not null and nombre !~ 'SIN NOMBRE\s*$'
),

palabras as (
    select n.edicion, n.cve_municipio, n.alcaldia, n.cve_col, n.colonia, p.palabra
    from nombres n
    cross join lateral (
        select distinct palabra
        from regexp_split_to_table(upper(unaccent(n.nombre)), '[^A-Z0-9Ñ]+') as palabra
    ) p
    where length(p.palabra) >= 3
      and p.palabra !~ '^[0-9]+$'
      and p.palabra not in ('DEL', 'LAS', 'LOS', 'CON', 'POR', 'PARA', 'UNA', 'UNO', 'SUS', 'QUE', 'THE', 'AND',
                            'SAPI', 'SAB', 'SRL', 'SCP', 'CIA', 'COMPANIA', 'SOCIEDAD', 'ANONIMA', 'CAPITAL',
                            'VARIABLE', 'RESPONSABILIDAD', 'LIMITADA', 'CIVIL', 'SUC', 'SUCURSAL', 'NUM', 'MEXICO')
),

conteos as (
    select edicion, 'ciudad'::text as nivel, '09'::text as cve_territorio, 'Ciudad de México'::text as territorio,
           palabra, count(*) as negocios
    from palabras group by 1, 5 having count(*) >= 5
    union all
    select edicion, 'alcaldia', cve_municipio, alcaldia, palabra, count(*)
    from palabras group by 1, 3, 4, 5 having count(*) >= 5
    union all
    select edicion, 'colonia', cve_col, colonia, palabra, count(*)
    from palabras where cve_col is not null group by 1, 3, 4, 5 having count(*) >= 3
)

select
    edicion, nivel, cve_territorio, territorio, palabra, negocios,
    palabra ~ '(ITO|ITA|ITOS|ITAS)$' and length(palabra) >= 5         as es_diminutivo,
    rank() over (partition by edicion, nivel, cve_territorio order by negocios desc)::int as lugar
from conteos

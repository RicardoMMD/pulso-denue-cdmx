-- Prototipo 1: compuerta de decisión del campo conglomerado (ver docs/Síntesis, "Cobertura del campo conglomerado").
-- Edición base 2026-05. Se ejecuta con `dbt compile` y se corre el SQL de target/ o directamente en psql.
--
-- Salida: una fila por métrica.
--   cobertura_campo        % de establecimientos con tipo y nombre de conglomerado (pertenencia por campo DENUE)
--   padron_espacial        % de mercados del padrón con un grupo MERCADO PUBLICO del DENUE que cruza su círculo y ≥10 locales
--   padron_nombre          ídem, y además con nombre parecido (similitud de trigramas ≥ 0.30 o contención de palabras)
-- Umbral de la compuerta: verde ≥ 70 %, ámbar 40–70 %, rojo < 40 % (sobre padron_nombre, la definición del documento).
with ed as (select '2026-05'::text as edicion),

grupos as (
    select m.tipo_denue, m.nombre_norm, m.grupo, count(*) as n_2026
    from {{ ref('conglomerado_campo_denue_miembro') }} m, ed
    where m.edicion = ed.edicion and m.tipo_denue = 'MERCADO PUBLICO'
    group by 1, 2, 3
),

grupos_geom as (
    select g.*, c.geom_utm
    from grupos g
    join {{ ref('conglomerado_campo_denue') }} c using (tipo_denue, nombre_norm, grupo)
),

padron as (
    select id_mercado,
           upper(unaccent(regexp_replace(mercado, '\s+', ' ', 'g'))) as nombre_norm,
           st_buffer(geom_utm, 1.5 * sqrt(superficie_m2 / pi())) as geom_utm
    from {{ ref('stg_mercados') }}
),

pareja as (
    select p.id_mercado,
           bool_or(g.n_2026 >= 10)                                                         as espacial_10,
           bool_or(g.n_2026 >= 10 and (similarity(p.nombre_norm, g.nombre_norm) >= 0.30
                                       or word_similarity(p.nombre_norm, g.nombre_norm) >= 0.60
                                       or word_similarity(g.nombre_norm, p.nombre_norm) >= 0.60)) as nombre_10
    from padron p
    left join grupos_geom g on st_intersects(p.geom_utm, g.geom_utm)
    group by 1
),

total as (select count(*) as n from core.denue_valido, ed where denue_valido.edicion = ed.edicion)

select 'cobertura_campo' as metrica,
       (select count(*) from {{ ref('conglomerado_campo_denue_miembro') }} m, ed where m.edicion = ed.edicion) as numerador,
       (select n from total) as denominador,
       round(100.0 * (select count(*) from {{ ref('conglomerado_campo_denue_miembro') }} m, ed where m.edicion = ed.edicion)
             / (select n from total), 1) as porcentaje
union all
select 'padron_espacial', count(*) filter (where espacial_10), count(*),
       round(100.0 * count(*) filter (where espacial_10) / count(*), 1) from pareja
union all
select 'padron_nombre', count(*) filter (where nombre_10), count(*),
       round(100.0 * count(*) filter (where nombre_10) / count(*), 1) from pareja

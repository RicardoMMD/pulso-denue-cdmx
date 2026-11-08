{{ config(post_hook=["create index on {{ this }} (tipo_denue, nombre_norm, x, y)"]) }}

-- Conglomerados declarados en el DENUE (campos tipo y nombre de centro comercial), agrupados por
-- (tipo, nombre normalizado). Un mismo nombre en lugares distintos se separa por distancia: puntos a
-- menos de 200 m forman un grupo (ST_ClusterDBSCAN). Se trabaja sobre ubicaciones únicas.
-- Se ignoran los nombres genéricos: "SIN NOMBRE", "NINGUNO" y los que solo repiten el tipo. Esos establecimientos
-- (unos 5 mil por edición) no forman conglomerado por campo; los puede cubrir una fuente espacial.
with miembros as (
    select
        tipo_centro_comercial                                                    as tipo_denue,
        upper(regexp_replace(unaccent(trim(centro_comercial)), '\s+', ' ', 'g')) as nombre_norm,
        round(st_x(geom_utm)::numeric, 2)                                         as x,
        round(st_y(geom_utm)::numeric, 2)                                         as y
    from {{ ref('denue_valido') }}
    where tipo_centro_comercial is not null and centro_comercial is not null
),

utiles as (
    select * from miembros
    where length(nombre_norm) >= 4
      and nombre_norm not in ('NINGUNO', 'OTRO', 'NO ESPECIFICADO', 'NO APLICA', 'SIN DATO', 'NA', 'N A')
      and nombre_norm not like '%SIN NOMBRE%'
      -- nombres que solo repiten el tipo ("PLAZA COMERCIAL", "EDIFICIO", "TORRE A", "CENTRAL DE ABASTOS")
      and nombre_norm !~ '^(EDIFICIO|PLAZA|TORRE|CENTRO|LOCAL|LOCALES|MERCADO|PASAJE|CENTRAL|OFICINAS)( (A|B|C|1|2|COMERCIAL|COMECIAL|PUBLICO|DE ABASTOS?|DE OFICINAS|Y PLAZA COMERCIAL|Y DE SERVICIOS?|COMERCIALES))*$'
),

puntos as (
    select distinct tipo_denue, nombre_norm, x, y from utiles
)

select
    tipo_denue, nombre_norm, x, y,
    st_clusterdbscan(st_setsrid(st_makepoint(x, y), 32614), eps := 200, minpoints := 1)
        over (partition by tipo_denue, nombre_norm) as grupo
from puntos

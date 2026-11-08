-- Falla si alguna tabla de semantic repite su grano declarado.
select 'establecimiento' as tabla, edicion || '|' || id_denue as llave, count(*) as filas
from {{ ref('establecimiento') }} group by 1, 2 having count(*) > 1
union all
select 'territorio', nivel || '|' || cve_territorio, count(*) from {{ ref('territorio') }} group by 1, 2 having count(*) > 1
union all
select 'actividad', version_scian || '|' || clase_scian, count(*) from {{ ref('actividad') }} group by 1, 2 having count(*) > 1
union all
select 'perfil_sector', edicion || '|' || nivel || '|' || cve_territorio || '|' || cve_sector, count(*) from {{ ref('perfil_sector') }} group by 1, 2 having count(*) > 1
union all
select 'conteo_clase', edicion || '|' || nivel || '|' || cve_territorio || '|' || version_scian || '|' || clase_scian, count(*) from {{ ref('conteo_clase') }} group by 1, 2 having count(*) > 1
union all
select 'calle', edicion || '|' || cve_municipio || '|' || calle_norm, count(*) from {{ ref('calle') }} group by 1, 2 having count(*) > 1
union all
select 'conglomerado', edicion || '|' || clave_conglomerado, count(*) from {{ ref('conglomerado') }} group by 1, 2 having count(*) > 1
union all
select 'dinamica', edicion || '|' || cve_municipio || '|' || cve_macrosector, count(*) from {{ ref('dinamica') }} group by 1, 2 having count(*) > 1
union all
select 'resumen_territorio', edicion || '|' || nivel || '|' || cve_territorio, count(*) from {{ ref('resumen_territorio') }} group by 1, 2 having count(*) > 1
union all
select 'censo_sector', nivel || '|' || cve_territorio || '|' || cve_sector, count(*) from {{ ref('censo_sector') }} group by 1, 2 having count(*) > 1
union all
select 'metro_estacion', edicion || '|' || estacion_norm || '|' || radio_m, count(*) from {{ ref('metro_estacion') }} group by 1, 2 having count(*) > 1
union all
select 'metro_linea', edicion || '|' || cve_linea || '|' || radio_m, count(*) from {{ ref('metro_linea') }} group by 1, 2 having count(*) > 1
union all
select 'metro_recorrido', cve_linea || '|' || estacion_norm, count(*) from {{ ref('metro_recorrido') }} group by 1, 2 having count(*) > 1
union all
select 'colonia_gemela', edicion || '|' || cve_col || '|' || lugar, count(*) from {{ ref('colonia_gemela') }} group by 1, 2 having count(*) > 1
union all
select 'palabra_nombre', edicion || '|' || nivel || '|' || cve_territorio || '|' || palabra, count(*) from {{ ref('palabra_nombre') }} group by 1, 2 having count(*) > 1


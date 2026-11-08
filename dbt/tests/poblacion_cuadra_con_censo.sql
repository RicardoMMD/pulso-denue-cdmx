-- La población ubicada (manzanas + localidades rurales) debe cuadrar con el total oficial del Censo 2020 por
-- alcaldía (ITER) con una tolerancia de 0.5 %: la diferencia son localidades de una o dos viviendas sin ubicación
-- y diferencias menores entre los archivos de INEGI.
with ubicada as (
    select cve_municipio, sum(poblacion) as poblacion from {{ ref('poblacion_unidad') }} group by 1
)
select a.cve_municipio, a.nombre_alcaldia, a.poblacion_2020, u.poblacion as ubicada
from {{ ref('dim_alcaldia') }} a
left join ubicada u using (cve_municipio)
where u.poblacion is null or abs(u.poblacion - a.poblacion_2020) > 0.005 * a.poblacion_2020

{{ config(post_hook=["create index on {{ this }} (edicion, cve_col)"]) }}

-- Colonias gemelas: las 5 colonias con el perfil sectorial más parecido a cada colonia (similitud coseno
-- entre sus participaciones por sector; 1 = mismo perfil). Grano: edición × colonia × gemela.
-- Solo colonias con 30 o más establecimientos, para que el perfil no sea ruido.
-- sectores_que_explican: los tres sectores que más aportan a la similitud, para explicar por qué se parecen.
--
-- Cálculo: el perfil de cada colonia es un vector de participaciones por sector. Se normaliza una vez por colonia
-- y la similitud de cada par es el producto punto de los vectores normalizados (cruce por sector compartido).
-- Los sectores que explican se calculan solo para los pares del top 5, cruzando sus dos vectores: volver a
-- cruzar todos los pares (decenas de millones de filas) dependía de las estimaciones del planificador y llegó a
-- tardar más de 55 minutos (14 nov 2026).
with perfiles as (
    select edicion, cve_territorio as cve_col, territorio as colonia, alcaldia, cve_sector, nombre_sector, participacion
    from {{ ref('perfil_sector') }}
    where nivel = 'colonia' and establecimientos_territorio >= 30
),

-- norma de cada vector: raíz de la suma de cuadrados de sus participaciones
normas as (
    select edicion, cve_col, sqrt(sum(participacion * participacion)) as norma
    from perfiles
    group by 1, 2
),

-- vectores normalizados (una fila por colonia y sector)
vectores as (
    select p.edicion, p.cve_col, p.cve_sector, p.participacion / n.norma as w
    from perfiles p
    join normas n using (edicion, cve_col)
),

-- producto punto de cada par de colonias que comparten al menos un sector
similitud as (
    select a.edicion, a.cve_col as cve_col, b.cve_col as cve_col_gemela, sum(a.w * b.w) as similitud
    from vectores a
    join vectores b
      on b.edicion = a.edicion and b.cve_sector = a.cve_sector and b.cve_col <> a.cve_col
    group by 1, 2, 3
),

top as (
    select *, row_number() over (partition by edicion, cve_col order by similitud desc, cve_col_gemela) as lugar
    from similitud
),

top5 as (
    select * from top where lugar <= 5
),

-- los tres sectores que más aportan a cada par del top 5: solo se cruzan los dos vectores del par
aportes as (
    select t.edicion, t.cve_col, t.cve_col_gemela, a.cve_sector, a.w * b.w as aporte,
           row_number() over (partition by t.edicion, t.cve_col, t.cve_col_gemela
                              order by a.w * b.w desc, a.cve_sector) as rn
    from top5 t
    join vectores a on a.edicion = t.edicion and a.cve_col = t.cve_col
    join vectores b on b.edicion = t.edicion and b.cve_col = t.cve_col_gemela and b.cve_sector = a.cve_sector
),

motivo as (
    select a.edicion, a.cve_col, a.cve_col_gemela,
           string_agg(s.nombre_sector, '; ' order by a.rn) as sectores_que_explican
    from aportes a
    join (select distinct cve_sector, nombre_sector from perfiles) s using (cve_sector)
    where a.rn <= 3
    group by 1, 2, 3
),

nombres as (
    select distinct edicion, cve_col, colonia, alcaldia from perfiles
)

select
    t.edicion,
    t.cve_col,
    ca.colonia,
    ca.alcaldia,
    t.lugar,
    t.cve_col_gemela,
    cb.colonia                                  as colonia_gemela,
    cb.alcaldia                                 as alcaldia_gemela,
    round(t.similitud::numeric, 4)              as similitud,
    m.sectores_que_explican
from top5 t
join nombres ca on ca.edicion = t.edicion and ca.cve_col = t.cve_col
join nombres cb on cb.edicion = t.edicion and cb.cve_col = t.cve_col_gemela
left join motivo m on m.edicion = t.edicion and m.cve_col = t.cve_col and m.cve_col_gemela = t.cve_col_gemela

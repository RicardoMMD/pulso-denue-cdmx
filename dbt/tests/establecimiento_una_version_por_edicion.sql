-- Falla si en alguna edición un establecimiento cae en más de una versión de la dimensión SCD2.
select sk_entidad, e.sk_edicion, count(*) as versiones
from {{ ref('dim_establecimiento') }} d
join {{ ref('dim_edicion') }} e on e.sk_edicion between d.desde_ordinal and d.hasta_ordinal
group by 1, 2
having count(*) > 1

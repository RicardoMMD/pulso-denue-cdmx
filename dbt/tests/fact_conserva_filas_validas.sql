-- Falla si el hecho no tiene exactamente un registro por establecimiento válido y edición,
-- o si lo excluido más lo cargado no suma lo que hay en staging.
with hecho as (select sk_edicion, count(*) n from {{ ref('fact_establecimiento') }} group by 1),
     esperado as (select ordinal as sk_edicion, count(*) n from {{ ref('denue_valido') }} group by 1),
     origen as (select e.sk_edicion, count(*) n from {{ ref('stg_denue') }} s join {{ ref('dim_edicion') }} e using (edicion) group by 1),
     excluido as (select e.sk_edicion, count(*) n from {{ ref('registro_excluidos') }} x join {{ ref('dim_edicion') }} e using (edicion) group by 1)
select o.sk_edicion, o.n as origen, h.n as hecho, coalesce(x.n, 0) as excluidos
from origen o
left join hecho h using (sk_edicion)
left join excluido x using (sk_edicion)
where h.n is distinct from o.n - coalesce(x.n, 0)

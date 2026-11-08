-- La dinámica cuadra con los totales: en cada edición N,
--   permanecen + nuevos + reaparecen = establecimientos de N
--   permanecen + bajas               = establecimientos de N-1
with d as (
    select edicion, sum(permanecen) p, sum(nuevos) n, sum(reaparecen) r, sum(bajas) b
    from {{ ref('dinamica') }} group by 1
),
e as (
    select edicion, establecimientos, lag(establecimientos) over (order by edicion) as anterior
    from {{ ref('edicion') }}
)
select d.*, e.establecimientos, e.anterior
from d join e using (edicion)
where d.p + d.n + d.r <> e.establecimientos
   or d.p + d.b <> e.anterior

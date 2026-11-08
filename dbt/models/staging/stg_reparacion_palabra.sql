{{ config(post_hook=["create unique index on {{ this }} (danada)"]) }}

-- Diccionario de reparación de palabras con mojibake del DENUE (ver macro reparar_texto).
-- Palabra dañada: contiene "Ã?" (letra perdida) tras la reparación determinista. Se repara con la palabra limpia
-- más frecuente del propio DENUE (todas las ediciones y columnas de texto, incluido el nombre de actividad, que
-- trae acentos) que tenga una letra latina acentuada (À..ÿ) en cada posición perdida.
{% set columnas = ['nom_estab', 'raz_social', 'nombre_act', 'nom_vial', 'nom_v_e_1', 'nom_v_e_2', 'nom_v_e_3',
                   'nomb_asent', 'nom_cencom', 'edificio', 'localidad', 'municipio'] %}

with textos as (
    {% for c in columnas %}
    select {{ c }} as texto from {{ source('raw', 'denue') }} where {{ c }} is not null
    {% if not loop.last %}union all{% endif %}
    {% endfor %}
),

vocabulario as (
    select palabra, count(*) as frecuencia
    from textos, regexp_split_to_table(upper(texto), '[^A-Z0-9À-ÿ]+') as palabra
    where palabra <> '' and palabra !~ '[ÃÂÿ]'
    group by 1
),

danadas as (
    select distinct palabra as danada
    from textos, regexp_split_to_table({{ reparar_mojibake_determinista('texto') }}, ' ') as palabra
    where texto ~ '{{ patron_mojibake() }}' and palabra ~ 'Ã\?'
),

partes as (
    -- separa signos al inicio y al final ("COMUNICACIÃ?N," → "" + "COMUNICACIÃ?N" + ",")
    select danada,
           substring(danada from '^[^A-Za-z0-9À-ÿ]*')                    as prefijo,
           substring(danada from '[^A-Za-z0-9À-ÿ?]*$')                   as sufijo
    from danadas
),

nucleo as (
    select danada, prefijo, sufijo,
           substr(danada, length(prefijo) + 1, length(danada) - length(prefijo) - length(sufijo)) as centro
    from partes
),

patrones as (
    select danada, prefijo, sufijo,
           replace(upper(centro), 'Ã?', '_')                          as patron_like,
           '^' || replace(upper(centro), 'Ã?', '[À-ÿ]') || '$'        as patron_regex
    from nucleo
    -- solo núcleos con letras, dígitos y las marcas de letra perdida
    where upper(centro) ~ '^([A-Z0-9À-ÿ]|Ã\?)+$'
)

select distinct on (p.danada)
    p.danada,
    p.prefijo || v.palabra || p.sufijo as reparada,
    v.frecuencia
from patrones p
join vocabulario v on v.palabra like p.patron_like and v.palabra ~ p.patron_regex
order by p.danada, v.frecuencia desc, v.palabra

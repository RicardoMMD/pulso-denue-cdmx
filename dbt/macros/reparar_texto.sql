{# Reparación de mojibake del DENUE: texto UTF-8 que INEGI volvió a codificar como latin-1 ("CARTÃ?N").
   Cada letra acentuada (2 bytes en UTF-8, C3 xx) quedó como "Ã" + el carácter latin-1 del segundo byte.

   1. Determinista: si el segundo byte sobrevivió (U+0080..U+00BF), "Ã" + ese carácter vuelve a su letra
      (Ã + U+008D = Í). Igual "Â" + U+00A0..U+00BF (bytes C2 xx) = ese carácter.
   2. Por vocabulario: si INEGI cambió el segundo byte por "?" (o por un espacio), la letra se perdió. Se infiere
      palabra por palabra con stg_reparacion_palabra (la palabra limpia más frecuente del DENUE que encaja).
   Lo que no se puede reparar queda con "Ã" y la bandera texto_danado de stg_denue. #}

{# Detecta texto con mojibake #}
{% macro patron_mojibake() -%}[ÃÂ]|ÿ[Â¿]{%- endmacro %}

{% macro reparar_mojibake_determinista(columna) -%}
{%- set ns = namespace(expr=columna) -%}
{%- for i in range(128, 192) -%}
{%- set ns.expr = "replace(" ~ ns.expr ~ ", 'Ã' || chr(" ~ i ~ "), chr(" ~ (i + 64) ~ "))" -%}
{%- endfor -%}
{%- for i in range(160, 192) -%}
{%- set ns.expr = "replace(" ~ ns.expr ~ ", 'Â' || chr(" ~ i ~ "), chr(" ~ i ~ "))" -%}
{%- endfor -%}
{#- letra perdida, marcada como "Ã?": un espacio tras "Ã" seguido de letra, una "Ã" sin segundo byte
    ("ÃLAMOS") y la doble codificación "ÿÂ" / "ÿ¿" ("JUÿÂREZ", "REVOLUCIÿ¿N") -#}
regexp_replace(regexp_replace(regexp_replace({{ ns.expr }},
    'ÿ[Â¿]', 'Ã?', 'g'),
    'Ã (?=[A-Za-zÀ-ÿ])', 'Ã?', 'g'),
    'Ã(?!\?)', 'Ã?', 'g')
{%- endmacro %}

{% macro reparar_texto(columna) -%}
case
    when {{ columna }} ~ '{{ patron_mojibake() }}' then (
        select string_agg(coalesce(r.reparada, w.palabra), ' ' order by w.n)
        from regexp_split_to_table({{ reparar_mojibake_determinista(columna) }}, ' ') with ordinality as w(palabra, n)
        left join {{ ref('stg_reparacion_palabra') }} r on r.danada = w.palabra
    )
    else {{ columna }}
end
{%- endmacro %}

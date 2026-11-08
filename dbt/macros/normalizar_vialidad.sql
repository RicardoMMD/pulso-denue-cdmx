{# Normaliza un nombre de calle para compararlo entre DENUE y OpenStreetMap: mayúsculas, sin acentos, sin
   signos ni tipo de vialidad al inicio (CALLE, AVENIDA, AV, CALZADA...), espacios colapsados. #}
{% macro normalizar_vialidad(columna) -%}
nullif(trim(regexp_replace(
    regexp_replace(
        regexp_replace(upper(unaccent(coalesce({{ columna }}, ''))), '[^A-Z0-9 ]', ' ', 'g'),
        '^(CALLE|AVENIDA|AV|CALZADA|CALZ|BOULEVARD|BLVD|PROLONGACION|PROL|CERRADA|CDA|ANDADOR|CIRCUITO|CALLEJON|PRIVADA|PRIV|VIADUCTO|RETORNO|PASEO|CAMINO|CARRETERA|DIAGONAL|CIRCUNVALACION|PERIFERICO|AUTOPISTA|PEATONAL|AND) +',
        '', 'g'),
    ' +', ' ', 'g')), '')
{%- endmacro %}

{# Vialidad del DENUE normalizada; nula cuando el campo no nombra una calle (relleno del DENUE). #}
{% macro vialidad_denue_norm(columna) -%}
case
    when {{ normalizar_vialidad(columna) }} in ('NINGUNO', 'OTRO', 'OTRO ESPECIFIQUE', 'SIN REFERENCIA', 'MANZANA O EDIFICACION CONTIGUA', 'SIN NOMBRE', 'SIN NOMBRE DE VIALIDAD')
      or {{ normalizar_vialidad(columna) }} like 'LOCALIDAD %' then null
    else {{ normalizar_vialidad(columna) }}
end
{%- endmacro %}

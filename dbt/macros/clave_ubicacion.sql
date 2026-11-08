{# Clave natural de DIM_UBICACION: manzana + código postal + asentamiento. Se usa en la dimensión y en la tabla de hechos. #}
{% macro clave_ubicacion(cve_manzana, codigo_postal, tipo_asentamiento, colonia) -%}
md5(concat_ws('|', coalesce({{ cve_manzana }}, ''), coalesce({{ codigo_postal }}, ''), coalesce({{ tipo_asentamiento }}, ''), coalesce({{ colonia }}, '')))
{%- endmacro %}

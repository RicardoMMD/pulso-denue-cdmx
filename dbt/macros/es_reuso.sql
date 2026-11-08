{# ¿Dos registros con el mismo id DENUE son en realidad negocios distintos (id reasignado por INEGI)?
   Nombres sin parecido, rama distinta sin equivalencia SCIAN 2018→2023 y a más de 100 m.
   Requiere una CTE `equivalencia (clase_2018, clase_2023)` en el modelo que la usa (vinculo_edicion). #}
{% macro es_reuso(a, b) -%}
(greatest(coalesce(word_similarity({{ a }}.nombre_norm, {{ b }}.nombre_norm), 0),
          coalesce(word_similarity({{ b }}.nombre_norm, {{ a }}.nombre_norm), 0)) < 0.4
 and left({{ a }}.clase_scian, 4) <> left({{ b }}.clase_scian, 4)
 and not exists (select 1 from equivalencia q where q.clase_2018 = {{ b }}.clase_scian and q.clase_2023 = {{ a }}.clase_scian)
 and not st_dwithin({{ a }}.geom_utm, {{ b }}.geom_utm, 100))
{%- endmacro %}

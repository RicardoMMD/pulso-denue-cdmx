{# Usa el esquema indicado tal cual (staging, core, semantic) en vez de <perfil>_<esquema>. #}
{% macro generate_schema_name(custom_schema_name, node) -%}
  {{ custom_schema_name | trim if custom_schema_name is not none else target.schema }}
{%- endmacro %}

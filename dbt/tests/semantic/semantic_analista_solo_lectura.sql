-- El rol del Analista debe poder leer todas las tablas de semantic y nada de core, staging ni raw.
-- Falla con cada permiso que sobra o falta.
{% set analista = env_var('PULSO_ANALISTA_USER', 'pulso_analista') %}
select table_schema, table_name, 'falta SELECT' as problema
from information_schema.tables
where table_schema = 'semantic'
  and not has_table_privilege('{{ analista }}', quote_ident(table_schema) || '.' || quote_ident(table_name), 'SELECT')
union all
select table_schema, table_name, 'SELECT indebido'
from information_schema.tables
where table_schema in ('core', 'staging', 'raw')
  and has_table_privilege('{{ analista }}', quote_ident(table_schema) || '.' || quote_ident(table_name), 'SELECT')

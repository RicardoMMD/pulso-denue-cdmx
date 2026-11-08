-- Pulso DENUE CDMX — arranque de la base en el clúster PostgreSQL 18 del VPS
--
-- Requisito del sistema: clúster 18 en el puerto 5433 con PostGIS y pgvector
-- instalados; ver INSTALAR_POSTGRES18.md.
--
-- Ejecución (como superusuario, en el VPS). Las contraseñas se pasan con -v
-- para que nunca queden en el repositorio:
--   sudo -u postgres psql -p 5433 -f 00_bootstrap.sql \
--     -v pw_owner='...' -v pw_app='...' -v pw_analista='...'

\set ON_ERROR_STOP on

-- Roles ----------------------------------------------------------------------
-- pulso_owner     dueño de todo; lo usan dbt y el pipeline
-- pulso_app       backend FastAPI: lee semantic, lee y escribe app
-- pulso_analista  SQL generado por el Analista: solo lectura de semantic

CREATE ROLE pulso_owner    LOGIN PASSWORD :'pw_owner';
CREATE ROLE pulso_app      LOGIN PASSWORD :'pw_app';
CREATE ROLE pulso_analista LOGIN PASSWORD :'pw_analista';

-- Base -----------------------------------------------------------------------

CREATE DATABASE pulso_denue OWNER pulso_owner ENCODING 'UTF8' TEMPLATE template0;
REVOKE ALL ON DATABASE pulso_denue FROM PUBLIC;
GRANT CONNECT ON DATABASE pulso_denue TO pulso_app, pulso_analista;
ALTER DATABASE pulso_denue SET timezone = 'America/Mexico_City';

\connect pulso_denue

-- Extensiones ----------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;     -- perfiles de colonia y RAG
CREATE EXTENSION IF NOT EXISTS pg_trgm;    -- búsqueda por nombre, resolver lugar
CREATE EXTENSION IF NOT EXISTS unaccent;   -- normalización de nombres

-- Esquemas -------------------------------------------------------------------

REVOKE CREATE ON SCHEMA public FROM PUBLIC;

CREATE SCHEMA raw      AUTHORIZATION pulso_owner;
CREATE SCHEMA staging  AUTHORIZATION pulso_owner;
CREATE SCHEMA core     AUTHORIZATION pulso_owner;
CREATE SCHEMA semantic AUTHORIZATION pulso_owner;
CREATE SCHEMA app      AUTHORIZATION pulso_owner;

-- Permisos: semantic, lectura para el backend y el Analista
GRANT USAGE ON SCHEMA semantic TO pulso_app, pulso_analista;
ALTER DEFAULT PRIVILEGES FOR ROLE pulso_owner IN SCHEMA semantic
  GRANT SELECT ON TABLES TO pulso_app, pulso_analista;

-- Permisos: app, lectura y escritura solo para el backend
GRANT USAGE ON SCHEMA app TO pulso_app;
ALTER DEFAULT PRIVILEGES FOR ROLE pulso_owner IN SCHEMA app
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO pulso_app;
ALTER DEFAULT PRIVILEGES FOR ROLE pulso_owner IN SCHEMA app
  GRANT USAGE, SELECT ON SEQUENCES TO pulso_app;

-- Topes por rol --------------------------------------------------------------

ALTER ROLE pulso_owner    IN DATABASE pulso_denue SET search_path = core, staging, raw, public;
ALTER ROLE pulso_app      IN DATABASE pulso_denue SET search_path = app, semantic, public;
ALTER ROLE pulso_app      IN DATABASE pulso_denue SET statement_timeout = '15s';
ALTER ROLE pulso_analista IN DATABASE pulso_denue SET search_path = semantic, public;
ALTER ROLE pulso_analista IN DATABASE pulso_denue SET statement_timeout = '8s';
ALTER ROLE pulso_analista IN DATABASE pulso_denue SET default_transaction_read_only = on;
ALTER ROLE pulso_analista CONNECTION LIMIT 10;

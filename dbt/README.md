# dbt — Pulso DENUE CDMX

Construye `staging` y `core` en la base `pulso_denue` (clúster 18 del VPS).

```bash
ssh -f -N -L 55432:localhost:5433 vps          # túnel
cd pipeline && set -a && . ../.env && set +a
uv run python cargar_raw.py 2026-05 ../data/raw/vigente/conjunto_de_datos/denue_inegi_09_.csv 2026-05-20   # DENUE a raw
uv run python cargar_externas.py                                                                          # colonias, mercados, tianguis a raw
uv run python cargar_osm_comercio.py                                                                      # áreas comerciales de OSM a raw
uv run python cargar_ce.py                                                                                # Censos Económicos 2024 a raw
uv run python descargar_osm_calles.py && uv run python cargar_osm_calles.py                               # calles de OpenStreetMap a raw
uv run dbt seed  --project-dir ../dbt --profiles-dir ../dbt
uv run dbt build --project-dir ../dbt --profiles-dir ../dbt
```

## Modelos

| Capa | Modelo | Contenido |
|---|---|---|
| staging | `stg_denue` | Tipos y texto limpios, geometría, bandera `coord_en_cdmx` |
| core | `denue_valido` | Staging sin puntos fuera de CDMX; UTM 14N y nombre normalizado |
| core | `registro_excluidos` | Lo que se dejó fuera y el motivo (18 filas en las 4 ediciones) |
| core | `vinculo_edicion` | Reconciliación entre ediciones: `id`, `difuso` (nombre + clase + 30 m), `id_salto` (reaparece tras faltar ediciones), `id_reusado` (mismo id, otro negocio) o `ninguno` |
| core | `entidad_establecimiento` | Identidad estable a lo largo de las ediciones |
| core | `dim_establecimiento` | SCD tipo 2: versiones, vigencia, edición de alta y de baja |
| core | `dim_edicion`, `dim_estrato`, `dim_actividad`, `dim_scian_sector`, `dim_alcaldia`, `dim_ageb`, `dim_ubicacion` | Dimensiones |
| staging | `stg_metro`, `stg_mg2020_*`, `stg_censo2020_*` | Metro de OSM, Marco Geoestadístico 2020 y Censo 2020 por manzana, localidad y alcaldía |
| staging | `stg_reparacion_palabra` | Diccionario para reparar letras dañadas (mojibake) del DENUE |
| staging | `stg_colonias`, `stg_mercados` | Catálogo de colonias y padrón de mercados de datos abiertos CDMX |
| core | `dim_colonia`, `asignacion_colonia` | Colonia por punto en polígono (98.8 %), la más cercana a menos de 50 m (0.4 %) o por nombre parecido (0.2 %); el resto, "sin colonia (<alcaldía>)". Banderas de coherencia con la alcaldía del DENUE |
| core | `dim_conglomerado`, `puente_establecimiento_conglomerado` | 5 993 conglomerados de cinco fuentes (campo del DENUE, padrón de mercados, OpenStreetMap, tianguis, mercados sobre ruedas); el puente guarda todas las pertenencias y marca un conglomerado principal |
| core | `dim_macrosector` | 7 macrosectores del portal (la agrupación vive en las semillas `ref_macrosector` y `ref_scian_sector`) |
| core | `scian_correspondencia` | Clases SCIAN 2018 → 2023 (tabla comparativa oficial de INEGI) |
| staging | `stg_ce2024`, `stg_ce_catalogo_actividad`, `stg_ce_variable` | Censos Económicos 2024 (CDMX), su catálogo de actividades y su diccionario |
| core | `fact_censo_economico`, `dim_ce_variable` | Censo por alcaldía × actividad × estrato, con 107 variables y su diccionario |
| core | `validacion_denue_censo` | DENUE contra Censo por edición × alcaldía × sector |
| staging | `stg_osm_calles` | Calles de OpenStreetMap con nombre normalizado y geometría UTM |
| core | `tramo_corte`, `dim_tramo`, `asignacion_tramo_punto`, `asignacion_tramo` | Calles cortadas en cuadras (241 mil dentro de CDMX) y tramo de cada establecimiento: 76.7 % por nombre, 6.8 % por nombre parecido, 15.1 % por cercanía |
| core | `fact_establecimiento` | Un registro por establecimiento y edición |

## Capa `semantic`

Única superficie del Analista (rol `pulso_analista`: solo lectura, 8 s por consulta) y fuente de las cifras de historias y fichas. Tablas materializadas, sin llaves sustitutas (solo claves naturales), con cada tabla y columna documentada en `models/semantic/_semantic.yml` y escrita como `COMMENT` en PostgreSQL (`persist_docs`), para que el Analista lea el catálogo desde la base. Permisos de `SELECT` para `pulso_app` y `pulso_analista` en cada construcción.

| Tabla | Grano | Para |
|---|---|---|
| `edicion` | edición | Edición vigente, fecha de corte, versión SCIAN, comparabilidad |
| `establecimiento` | edición × establecimiento | Toda pregunta sobre negocios: actividad, alcaldía, colonia, calle, conglomerado, contacto, punto (`geom`) |
| `territorio` | ciudad, alcaldía o colonia | Resolver lugar (`nombre_norm` con trigramas) |
| `actividad` | versión SCIAN × clase | Traducir giro a clase SCIAN |
| `perfil_sector` | edición × alcaldía o colonia × sector | ADN de cada alcaldía, Colonias gemelas (cociente de localización) |
| `conteo_clase` | edición × ciudad o alcaldía × clase | Rarezas, rankings de giros |
| `calle` | edición × alcaldía × calle | Las calles hablan (giro dominante) |
| `conglomerado` | edición × conglomerado | Ciudades dentro de la ciudad |
| `dinamica` | edición × alcaldía × macrosector | Altas, bajas, reapariciones |
| `resumen_territorio` | edición × ciudad o alcaldía | Fichas por alcaldía, presencia digital |
| `censo_sector` | ciudad o alcaldía × sector | Censos Económicos 2024 con nombres legibles |
| `cobertura_censo` | edición × alcaldía × sector | Qué tan completo es el DENUE frente al Censo |

Pruebas propias: `semantic_paridad_conteos` (cada agregado suma lo mismo que el hecho), `semantic_dinamica_cuadra` (permanecen + nuevos + reaparecen = edición actual; permanecen + bajas = anterior), `semantic_granos_unicos` y `semantic_analista_solo_lectura` (el Analista lee todo `semantic` y nada de `core`, `staging` ni `raw`).

Tablas añadidas después: `metro_estacion` (ranking por estación, radios de 300, 500 y 800 m), `metro_linea` (unión de radios por línea), `metro_recorrido` (orden de estaciones), `colonia_gemela` (5 colonias más parecidas por perfil sectorial, con los sectores que explican el parecido) y `palabra_nombre` (palabras de los nombres por territorio). `territorio` y `resumen_territorio` llevan población del Censo 2020 y densidad.

Pendiente: Islas de 15 minutos (falta la red peatonal de OpenStreetMap y el cálculo de isócronas). La similitud de `colonia_gemela` usa participaciones crudas, así que casi todos los pares salen con similitud alta; revisar si conviene centrar o usar el cociente de localización.

## Pendiente en core

- Nombres SCIAN 2018 de subsector, rama y subrama: hoy son los de SCIAN 2023 (catálogo del Censo).
- Red peatonal (banquetas y veredas) para las Islas de 15 minutos.
- Reconciliar conglomerados repetidos (el mismo mercado en el DENUE, el padrón y OSM).
- Banderas de redes sociales y de coordenada centroide: el DENUE no las trae.

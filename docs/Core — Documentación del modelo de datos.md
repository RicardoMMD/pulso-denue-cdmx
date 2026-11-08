# Core: documentación del modelo de datos

Estado al 2026-11-08 (con tramos de calle). Base `pulso_denue`, clúster PostgreSQL 18 del VPS (`localhost:5433`), construida con dbt desde `dbt/`.

Este documento describe lo que contiene el esquema `core`, cómo se construyó, qué decisiones se tomaron y qué falta. Para correr el proyecto, ver [dbt/README.md](../dbt/README.md). Para el origen de los archivos descargados, ver [data/raw/MANIFEST.md](../data/raw/MANIFEST.md).

## 1. Qué es `core`

`core` es el modelo analítico del proyecto: un esquema en estrella con grano de **un establecimiento por edición del DENUE**, con dimensiones normalizadas (copo de nieve) para geografía y actividad económica, y con historial de cada establecimiento (SCD tipo 2).

Todo el esquema se reconstruye con dbt a partir de `raw`. No se escribe a mano.

Las capas del flujo de datos:

```
CSV de INEGI ──cargar_raw.py──▶ raw.denue ──▶ staging.stg_denue ──▶ core.*
GeoJSON CDMX ─cargar_externas.py▶ raw.colonias_cdmx / mercados_publicos / tianguis / mercados_sobre_ruedas ──▶ staging.stg_* ──▶ core.*
PDF de INEGI ──(extraído a CSV)──▶ dbt seed ──▶ core.ref_*
```

## 2. Datos de entrada

### Ediciones del DENUE (CDMX, entidad 09)

Cuatro ediciones, todas con las mismas 42 columnas (ISO-8859-1).

| Edición | Publicación | Filas en `raw` | Excluidas | En el modelo |
|---|---|---|---|---|
| 2024-05 | 2024-05-23 | 476 096 | 3 | 476 093 |
| 2024-11 | 2024-11-26 | 458 228 | 12 | 458 216 |
| 2025-05 | 2025-05-22 | 460 762 | 0 | 460 762 |
| 2026-05 | 2026-05-20 | 462 732 | 3 | 462 729 |
| **Total** | | **1 857 818** | **18** | **1 857 800** |

La edición 05/2026 es la base. La siguiente se publica el 2026-11-25.

### Fuentes externas

| Fuente | Contenido | Uso |
|---|---|---|
| Catálogo de colonias, datos abiertos CDMX (CC BY 4.0) | 1 543 polígonos: 1 262 colonias y 281 pueblos y barrios originarios | `dim_colonia`, asignación de colonia |
| Mercados públicos, datos abiertos CDMX (CC BY 4.0) | 329 puntos con superficie, locales y tipo | `dim_conglomerado` |
| Tianguis, datos abiertos CDMX (CC BY 4.0) | 1 367 puntos con día, horario y número de oferentes | `dim_conglomerado` |
| Mercados sobre ruedas, datos abiertos CDMX (CC BY 4.0) | 51 puntos con ruta, día y oferentes | `dim_conglomerado` |
| OpenStreetMap, áreas comerciales (ODbL) | 1 032 polígonos y puntos: centros comerciales, mercados y zonas de comercio (se omiten 21 relaciones) | `dim_conglomerado` |
| INEGI, Tabla comparativa SCIAN México 2023-2018 (PDF) | 265 vínculos de clases que cambian | `scian_correspondencia` |
| INEGI, Censos Económicos 2024, datos abiertos de CDMX | 46 062 filas: 16 alcaldías × actividad × estrato, 107 columnas (año de referencia 2023, SCIAN 2023) | `fact_censo_economico`, `validacion_denue_censo`, nombres de la jerarquía SCIAN |
| OpenStreetMap (Overpass API, ODbL) | 202 902 calles de CDMX y alrededores, 128 339 con nombre | `dim_tramo`, asignación de tramo |
| INEGI, catálogo de actividades del Censo | 1 932 códigos con nombre, de sector a clase | `dim_actividad` (nombres de subsector, rama y subrama) |

## 3. Capa `staging`

### `stg_denue`

Una fila por establecimiento y edición. Solo tipa y limpia; no decide nada de negocio.

- Tipos: `id_denue` a `bigint`, coordenadas a `numeric`, `geom` como `geometry(point, 4326)`.
- Texto: `trim` y cadenas vacías a `null`. Nombres de columna en español sin abreviaturas crípticas (`vialidad`, `colonia`, `codigo_postal`).
- Claves geográficas compuestas: `cve_mun_completa` (entidad + municipio) y `cve_manzana` (entidad + municipio + localidad + AGEB + manzana).
- `fecha_alta`: el formato normal es `AAAA-MM` y se convierte al día 1 del mes. Dos filas traen `06/10/2023` y se interpretan como `DD/MM/AAAA`. Variantes `AAAA MM` y `AAAA_MM` también se interpretan; ninguna fila queda sin fecha.
- Mojibake: INEGI trae letras acentuadas dañadas ("CARTÃ?N") en ~1 200 filas. `reparar_texto` las repara en nombre, razón social, vialidades, edificio, colonia y centro comercial: primero los bytes que sobrevivieron, y si la letra se perdió, con `stg_reparacion_palabra` (la palabra limpia más frecuente del DENUE que encaja, 48 palabras). Quedan 12 filas sin reparar, marcadas con `texto_danado`.
- Bandera `coord_en_cdmx`: verdadera si la latitud está entre 19.0 y 19.65 y la longitud entre -99.40 y -98.90.

### `stg_colonias`

Polígonos válidos (`st_makevalid`, solo polígonos, multipolígono), en grados y en UTM 14N. El catálogo traía un polígono inválido.

### `stg_mercados`

Mercados con tipos numéricos, `id_mercado` secuencial, geometría en grados y en UTM 14N.

## 4. Capa `core`: modelos

### 4.1 Preparación

**`denue_valido`.** `stg_denue` sin los puntos fuera de CDMX. Agrega:
- `ordinal`: orden cronológico de la edición (1 a 4).
- `geom_utm`: la geometría en UTM 14N (EPSG:32614), en metros.
- `nombre_norm`: nombre en mayúsculas, sin acentos y con espacios colapsados; lo usa la reconciliación difusa.

Tiene índices en `geom_utm` (GiST) y en `(edicion, id_denue)`.

**`registro_excluidos`.** Qué se dejó fuera y por qué. Hoy son 18 filas, todas con motivo "coordenada fuera de CDMX": 3 en la 05/2024, 12 en la 11/2024, 0 en la 05/2025 y 3 en la 05/2026. Los puntos caen en lugares como Baja California o Yucatán, es decir, son errores de geocodificación de INEGI.

> **Decisión (2026-11-07):** excluir esos puntos en lugar de reubicarlos. Se aplicó a las cuatro ediciones, no solo a la vigente.

### 4.2 Reconciliación entre ediciones

**`vinculo_edicion`.** Una fila por establecimiento y edición. Dice cómo se enlaza con la edición anterior:

| Método | Regla |
|---|---|
| `id` | Mismo id DENUE en la edición inmediata anterior |
| `difuso` | Id distinto, pero mismo nombre normalizado, misma clase SCIAN y menos de 30 m. Uno a uno: primero el candidato más cercano por registro nuevo, luego el más cercano por registro viejo |
| `id_salto` | Mismo id DENUE en una edición anterior no inmediata: faltó y volvió. Se vincula a su última aparición |
| `ninguno` | Alta nueva (o primera edición de la serie) |

El nombre nulo no entra al emparejamiento difuso. El difuso acepta clases equivalentes entre SCIAN 2018 y 2023 (`scian_correspondencia`).

Resultados:

| Edición | Mismo id | Difuso | Alta nueva |
|---|---|---|---|
| 2024-05 | — | — | 476 093 (primera edición) |
| 2024-11 | 323 474 | 967 (+533 `id_reusado`) | 133 242 |
| 2025-05 | 447 286 | 2 723 (+496 `id_salto`, 5 `id_reusado`) | 10 252 |
| 2026-05 | 453 045 | 146 (+2 092 `id_salto`, 7 `id_reusado`) | 7 439 |

`id_reusado`: el mismo id, pero es otro negocio (INEGI reasignó el id): nombres sin parecido (`word_similarity` < 0.4 en ambos sentidos), rama distinta sin equivalencia SCIAN 2018→2023 y a más de 100 m. Se trata como alta nueva y abre una entidad nueva.

La distancia promedio de los vínculos difusos es 2.5 m y el máximo 29.9 m.

**`entidad_establecimiento`.** Asigna a cada fila una identidad estable `sk_entidad` siguiendo la cadena de vínculos desde su alta, con una consulta recursiva. Un establecimiento que cambia de id por emparejamiento difuso conserva su `sk_entidad`. Hay 627 571 entidades distintas.

### 4.3 Dimensiones

| Modelo | Filas | Contenido |
|---|---|---|
| `dim_edicion` | 4 | `sk_edicion` (= orden cronológico), edición, año, mes, fecha de corte, versión SCIAN (deducida de los datos: `SCIAN 2018` en 05/2024, `SCIAN 2023` desde 11/2024), `proporcion_ids_nuevos` y `comparable_con_anterior` (falso si cambió la versión SCIAN o más del 10 % de los ids son nuevos: solo 11/2024, con 29 %), fecha de carga, filas de origen |
| `dim_estrato` | 7 | Etiqueta del DENUE, orden, límites inferior y superior, punto medio, y `id_estrato_ce`: el estrato equivalente del Censo (0-10, 11-50, 51-250, 251+). El estrato abierto "251 y más personas" no tiene límite superior ni punto medio |
| `dim_macrosector` | 7 | Macrosectores del portal: familias de sectores para leer la ciudad de un vistazo (ver 4.11) |
| `dim_scian_sector` | 23 | Sector (2 dígitos), nombre, sector agrupado (31-33, 48-49) y su macrosector |
| `dim_actividad` | 987 | Clase SCIAN (6 dígitos) y su nombre, subrama (5), rama (4), subsector (3), sector y macrosector, cada uno con código y nombre. Los nombres de subsector, rama y subrama vienen del catálogo de los Censos Económicos y son SCIAN 2023 (`version_nombres_jerarquia`); 14, 23 y 28 clases, respectivamente, no los tienen porque ese código no existe en 2023 |
| `dim_alcaldia` | 16 | Clave y nombre |
| `dim_ageb` | 2 722 | AGEB con su localidad y alcaldía |
| `dim_ubicacion` | 148 634 | Manzana + código postal + tipo de asentamiento + colonia según DENUE; llaves a AGEB y alcaldía |
| `dim_colonia` | 1 560 | 1 543 colonias del catálogo, 16 miembros "sin colonia (<alcaldía>)" (`sk_colonia` = -cve_municipio) y el miembro 0 "sin colonia"; `es_especial` los distingue; área en m² y geometría |
| `dim_conglomerado` | 5 994 | 5 993 conglomerados de cinco fuentes más el miembro 0 "sin asignar" (ver 4.6) |
| `dim_tramo` | 241 236 | Cuadras de OpenStreetMap dentro de CDMX más el miembro 0 "sin asignar" (ver 4.10) |
| `dim_ce_variable` | 107 | Diccionario de variables del Censo: código, descripción, unidad (millones de pesos, miles de horas, conteo) y rango válido |
| `dim_establecimiento` | 1 037 249 | Versiones SCD tipo 2 (ver 4.4) |

Notas de diseño:
- Los nombres de clase de `dim_actividad` son los de la edición más reciente donde aparece cada clase. Dentro de un mismo código nunca cambia el nombre entre ediciones.
- La jerarquía geográfica es copo de nieve: manzana → AGEB → localidad → alcaldía → entidad. La colonia es una jerarquía paralela (colonia → alcaldía).
- La clave natural de `dim_ubicacion` es un hash (`clave_ubicacion`) de manzana, código postal, tipo de asentamiento y colonia. El macro `clave_ubicacion` lo calcula igual en la dimensión y en el hecho.
- Las llaves sustitutas son enteros que se asignan por orden de la clave natural en cada reconstrucción. Por eso no son estables entre corridas; las tablas dependientes se reconstruyen juntas.

### 4.4 `dim_establecimiento` (SCD tipo 2)

Una fila por versión de un establecimiento. Cambia de versión cuando:
- cambia alguno de estos atributos: id DENUE, nombre, razón social, tipo de unidad, teléfono, correo, sitio web, edificio, piso o fecha de alta; o
- el establecimiento no estuvo en la edición inmediata anterior.

El `clee` no se sigue: cambia con cada reclasificación. Se conserva el valor de la primera edición de la versión.

Columnas de vigencia: `desde_ordinal` y `hasta_ordinal` (usadas para el join con el hecho), `vigente_desde` y `vigente_hasta` (edición, en texto), `edicion_alta` y `edicion_baja` (a nivel de establecimiento; la baja es la primera edición donde ya no aparece, y es nula si sigue en la última), y `es_vigente`.

Resultados:
- 627 571 establecimientos y 1 037 249 versiones.
- 462 729 siguen vigentes; 166 927 tienen baja: 151 146 en la 11/2024, 8 210 en la 05/2025 y 7 571 en la 05/2026.
- Versiones por establecimiento: 338 585 tienen 1, 183 870 tienen 2, 97 880 tienen 3 y 9 321 tienen 4.

### 4.5 Asignaciones

**`asignacion_colonia`.** Colonia de cada establecimiento y edición:

| Método | Regla | Peso en la 05/2026 |
|---|---|---|
| `poligono` | El punto cae dentro de un polígono; si cae en dos, el de menor área | 98.75 % (456 953) |
| `cercania` | Fuera de todo polígono, colonia más cercana a menos de 50 m | 0.41 % (1 907) |
| `nombre` | Fuera de todo polígono y lejos: la colonia que declara el DENUE se parece (trigramas ≥ 0.5) a una colonia del catálogo de la misma alcaldía a menos de 2 km; gana la más parecida | 0.22 % (1 026) |
| `ninguna` | Ninguna de las anteriores: miembro "sin colonia (<alcaldía>)", `sk_colonia = -cve_municipio` (por ejemplo -13 = Xochimilco); 0 si no hay alcaldía | 0.62 % (2 843) |

Los 2 843 sin colonia están sobre todo en Xochimilco (1 529), Tlalpan (384), Milpa Alta (365) y Tláhuac (259): zonas rurales que el catálogo no cubre. Para esas filas solo se conoce la alcaldía.

**Coherencia con la alcaldía del DENUE.** `alcaldia_colonia` compara la alcaldía de la colonia asignada con la que declara el DENUE: `coincide` (458 491 en la 05/2026), `frontera` (547: la colonia es de otra alcaldía, pero el punto está a 100 m o menos de la alcaldía declarada, ruido de límite) o `discrepante` (848: a más de 100 m; 311 de ellos a menos de 250 m). `distancia_alcaldia_declarada_m` guarda la distancia. La geometría de `dim_alcaldia` es la unión de las colonias, así que es aproximada; para límites oficiales hace falta el Marco Geoestadístico. Ninguna asignación se cambia: son banderas para filtrar.

Las 10 colonias del catálogo sin ningún establecimiento en la 05/2026 se conservan.

**`puente_establecimiento_conglomerado`.** Pertenencia de cada establecimiento a conglomerados (ver 4.6).

### 4.6 Conglomerados

Un conglomerado es un lugar donde el comercio o el equipamiento se agrupa: un mercado, una plaza, una central de abasto. Habilita "Ciudades dentro de la ciudad". `dim_conglomerado` reúne cinco fuentes; `conglomerado_fuente` las unifica con su geometría.

| Prioridad | Origen | Conglomerados | Cómo se asigna un establecimiento |
|---|---|---|---|
| 1 | **Campo del DENUE** (tipo y nombre de centro comercial) | 3 228 | Por campo: el propio DENUE lo declara |
| 2 | **Padrón de mercados públicos** CDMX | 329 | Espacial: dentro de un círculo de radio 1.5 × √(superficie/π) |
| 3 | **OpenStreetMap**: centros comerciales y mercados | 710 | Espacial: dentro del polígono (los puntos, círculo de 30 m) |
| 4 | **OpenStreetMap**: zonas comerciales (`landuse=retail`) | 308 | Espacial: dentro del polígono |
| 5 | **Tianguis** | 1 367 | Espacial: círculo de 40 m |
| 6 | **Mercados sobre ruedas** | 51 | Espacial: círculo de 40 m |

**Conglomerados del campo DENUE.** El DENUE trae, para unos 97 mil establecimientos por edición, el tipo de centro comercial y su nombre. Se agrupan por (tipo, nombre normalizado) y se separan por distancia: puntos a menos de 200 m forman un grupo (`ST_ClusterDBSCAN`), así que el mismo nombre en dos lugares distintos son dos conglomerados. Se conservan los que tienen al menos 3 establecimientos en alguna edición. La geometría es la envolvente convexa de sus puntos (todas las ediciones) más 15 m. Tipos más frecuentes: edificio comercial y de servicios (1 031), centro o plaza comercial (888), mercado público (791), pasaje o andador comercial (211), hospital o centro médico (112), central de abasto (42).

Se descartan los nombres genéricos: los que contienen "SIN NOMBRE" y los que solo repiten el tipo ("PLAZA COMERCIAL", "EDIFICIO", "TORRE A", "CENTRAL DE ABASTOS"). Son unos 5 mil establecimientos por edición que no forman conglomerado por campo.

**Puente y conglomerado principal.** Un establecimiento puede pertenecer a varios conglomerados a la vez (una tienda de un mercado público que además cae en una zona comercial de OSM). El puente guarda todas las pertenencias y marca una como `es_principal`: la de menor prioridad y, entre iguales, la de menor superficie. El hecho usa solo la principal. El puente tiene 637 032 filas en total (las cuatro ediciones). En la 05/2026, el 22.0 % de los establecimientos (101 580) tiene conglomerado principal.

> **Decisión:** tianguis y mercados sobre ruedas (prioridad 5 y 6) quedan en el puente pero **nunca son el conglomerado principal**. Son actividad temporal junto a comercios permanentes: etiquetar como "tianguis" a una tienda fija confundiría en la escena. Con ellos como principal, la cobertura habría sido del 23.5 %.

**Principal por origen en la 05/2026:** campo DENUE 94 529, padrón de mercados 4 681, OpenStreetMap 2 370. Por categoría: comercio 97 144, servicios y equipamiento 3 463, otro 819, industria 154.

**Radio de los mercados del padrón.** El padrón solo trae un punto por mercado, así que cada uno recibe un círculo. El radio se calibró contra el DENUE 05/2026: para cada regla se contaron los establecimientos dentro del círculo y se comparó con los locales del padrón (72 293 en total).

| Regla de radio | Establecimientos | Correlación con locales | Radio mediano |
|---|---|---|---|
| √(superficie/π) | 17 574 | 0.58 | 30 m |
| √(superficie/π) + 20 m | 40 884 | 0.70 | 50 m |
| **1.5 × √(superficie/π)** | 41 356 | **0.83** | 45 m |
| Fijo 60 m | 39 138 | 0.17 | 60 m |
| Fijo 100 m | 64 039 | 0.60 | 100 m |

Se eligió 1.5 × √(superficie/π) por la correlación. El conteo total queda por debajo de los locales del padrón (41 356 contra 72 293), brecha esperable: no todos los locales de un mercado tienen registro en el DENUE. Los radios de los tianguis (40 m) y de los puntos de OSM (30 m) no se calibraron; son supuestos.

**Límites que conviene conocer:**
- **Mercados repetidos.** Un mismo mercado puede aparecer hasta tres veces: en el campo del DENUE, en el padrón y en OpenStreetMap. No se fusionan; el principal es el del DENUE. Para contar mercados distintos hay que reconciliarlos antes (por distancia y nombre).
- **Nombres con variantes.** "Mercado Jamaica" y "Mercado Jamaica Vive" en el campo DENUE son dos conglomerados en el mismo lugar.
- **758 conglomerados sin establecimientos** en la 05/2026: sobre todo tianguis, mercados de OSM y puntos en zonas sin cobertura del DENUE. Se conservan.
- **Tianguis y mercados sobre ruedas** son lugares donde operan ciertos días, no establecimientos fijos. El DENUE no incluye comercio ambulante, así que la pertenencia mide los comercios permanentes cercanos, no a los oferentes.
- **Zonas comerciales de OSM** (`landuse=retail`) son áreas amplias y poco precisas: se excluyen las menores de 100 m² y las mayores de 2 km².
- **Relaciones de OSM omitidas** (21), por geometría compuesta.

### 4.7 Correspondencia SCIAN

**`scian_correspondencia`.** Para cada clase SCIAN 2018 del DENUE, su clase en SCIAN 2023. La tabla de INEGI solo lista las clases que cambian; las demás conservan código.

| Tipo | Clases | Significado |
|---|---|---|
| `igual` | 837 | No aparece en la tabla de cambios |
| `mismo codigo, cambia nombre o contenido` | 116 | Mismo código en 2023, con otro nombre o contenido |
| `cambia codigo` | 19 | Código nuevo |
| `parcial` | 15 | Se reparte en varias clases 2023 (columna `parte`, por ejemplo `1/84`) |

En la 05/2026, 219 470 establecimientos están en clases que cambian. Casi todo es una clase 2018 de comercio exclusivamente por internet que se reparte entre 84 clases 2023.

Solo aplica a las filas SCIAN 2018 de `dim_actividad` (hoy la edición 05/2024). Las demás ediciones ya vienen en SCIAN 2023. Para comparar a nivel de clase entre ediciones, usar `dim_actividad.clase_scian_2023` (nula cuando la clase 2018 se reparte en varias).

### 4.8 `fact_establecimiento`

Grano: un establecimiento por edición. 1 857 800 filas.

| Columna | Descripción |
|---|---|
| `sk_edicion`, `sk_ubicacion`, `sk_actividad`, `sk_estrato`, `sk_establecimiento`, `sk_colonia`, `sk_conglomerado`, `sk_tramo` | Llaves a las dimensiones. `sk_conglomerado` es 0 si no cae en ningún mercado; `sk_tramo` es 0 si no se encontró calle |
| `id_denue` | Dimensión degenerada |
| `cantidad` | Siempre 1, para contar |
| `longitud`, `latitud` | Coordenadas originales |
| `geom` | `geography(point, 4326)` |
| `x_m`, `y_m` | Metros en UTM 14N con origen en el Zócalo (19.4326, -99.1332) |
| `tiene_web`, `tiene_correo`, `tiene_telefono` | Banderas de contacto |
| `metodo_colonia`, `colonia_por_cercania`, `alcaldia_colonia`, `distancia_alcaldia_declarada_m`, `metodo_tramo`, `texto_danado` | Cómo se asignaron la colonia y el tramo de calle, coherencia con la alcaldía del DENUE y si queda texto dañado |

El hecho se une a la versión vigente de `dim_establecimiento` en esa edición (`ordinal` entre `desde_ordinal` y `hasta_ordinal`). Índices: edición, actividad, ubicación, establecimiento, colonia, conglomerado y GiST en `geom`.

### 4.9 Censos Económicos 2024

**`fact_censo_economico`.** 46 062 filas. Grano: territorio × actividad × estrato.

- **Territorio:** una de las 16 alcaldías (`sk_alcaldia`) o la entidad completa (`sk_alcaldia` nulo, `nivel_territorial = 'entidad'`).
- **Actividad:** código SCIAN 2023 en su nivel (`nivel_actividad`: total, sector, subsector, rama, subrama, clase). Hay 79 filas de total por alcaldía y nivel.
- **Estrato:** `id_estrato_ce` 1 a 4 (personal ocupado 0-10, 11-50, 51-250, 251+); nulo es la suma de estratos y 99 los estratos agrupados por confidencialidad (`tipo_estrato`: rango, suma, confidencial).
- **Variables:** las 107 columnas del archivo de INEGI con sus códigos (`ue`, `h001a` personal ocupado total, `a131a` valor agregado censal bruto, `a800a` ingresos totales, etc.); `dim_ce_variable` las describe. Las celdas vacías son confidenciales: el número de unidades económicas siempre se publica, las cifras económicas no.

**Cuidado al sumar.** Cada nivel de actividad y cada estrato repiten los mismos establecimientos. Hay que filtrar por `nivel_actividad` y `tipo_estrato` antes de agregar. Por ejemplo, el total de CDMX son 425 005 unidades con `nivel_actividad = 'total'`, `tipo_estrato = 'suma'`.

**`validacion_denue_censo`.** 1 221 filas: edición × alcaldía × sector, con unidades del DENUE, unidades del Censo, razón y diferencia. El sector se agrupa como el Censo (31-33, 48-49). Los sectores del DENUE que el Censo no cubre (gobierno, 93) salen con `en_alcance_censo = false`.

Razón DENUE / Censo en los sectores que cubre el Censo: 1,110 (05/2024), 1,069 (11/2024), 1,075 (05/2025) y 1,080 (05/2026). Detalle y lectura en [Ideas por profundizar](Ideas%20por%20profundizar.md).

**Prueba `denue_cercano_al_censo`.** Aviso, no falla la construcción: en la edición más reciente, el total por alcaldía no debe alejarse del Censo más de -10 % ni +25 %. Hoy las 16 alcaldías están entre 1,06 y 1,11.

### 4.10 Tramos de calle

**Cómo se hacen los tramos.** `tramo_corte` corta cada calle de OpenStreetMap en sus nodos compartidos con otra calle (los cruces) y en sus extremos, así que un tramo es una cuadra, de cruce a cruce. De 202 902 calles salen 433 732 tramos. `dim_tramo` conserva los que tienen su punto medio dentro de una colonia: 241 235.

- Atributos: nombre de la vialidad (puede ser nulo: 60 138 tramos no tienen nombre en OSM), nombre normalizado, tipo de vía, sentido único, velocidad máxima, longitud, colonia y geometría. Longitud media 68 m; red total de 16 348 km.
- Tipos: residencial 140 570, servicio 37 879, terciaria 24 259, secundaria 16 589, primaria 8 895, peatonal 2 934, más autopistas y enlaces.
- Descarga: solo calles transitables por vehículo y peatonales formales. No incluye banquetas ni veredas (`footway`, `path`, `steps`).

**Normalización de nombres.** El macro `normalizar_vialidad` pasa a mayúsculas, quita acentos y signos y elimina el tipo de vialidad al inicio (CALLE, AVENIDA, CALZADA…), para comparar "Calle Gobernación" de OSM con "GOBERNACION" del DENUE. `vialidad_denue_norm` además descarta rellenos del DENUE que no son calles ("MANZANA O EDIFICACION CONTIGUA", "SIN REFERENCIA", "LOCALIDAD 800", "NINGUNO", "OTRO").

**Asignación (`asignacion_tramo`).** Cada establecimiento recibe el tramo más cercano, con este orden de preferencia:

| Método | Regla | Peso en la 05/2026 |
|---|---|---|
| `nombre` | Tramo a 60 m o menos con el mismo nombre normalizado que la vialidad del DENUE | 76.7 % |
| `nombre_similar` | Similitud de trigramas ≥ 0.55 y los mismos números ("26 de enero" ≠ "25 de enero") | 6.8 % |
| `cercania` | Ningún nombre coincide: el tramo más cercano a 30 m o menos | 15.1 % |
| `ninguno` | Sin tramo (`sk_tramo = 0`) | 1.4 % |

Se evalúan los 15 tramos más cercanos de cada punto. Para no calcular 1.86 millones de veces, `asignacion_tramo_punto` trabaja sobre las 939 315 combinaciones únicas de vialidad y ubicación (un establecimiento conserva su punto entre ediciones). La distancia media al tramo es de unos 7 m. En la 05/2026 los establecimientos caen en 94 392 tramos distintos.

**Una limitación del método `cercania`.** Cuando el nombre del DENUE no coincide con ningún tramo cercano, se asigna la calle más próxima aunque se llame distinto. Por ejemplo, un establecimiento de "REFORMA" puede caer en "Calle Jesús Garibay" si esa es la calle bajo el punto. Para análisis por calle conviene filtrar `metodo_tramo in ('nombre', 'nombre_similar')`.

### 4.11 Macrosectores

Agrupación de los 23 sectores SCIAN en 7 familias, pensada para colorear la escena "Ciudad de luz" y para dar un primer nivel de lectura. Es decisión de diseño del portal (aprobada el 2026-11-08), no una clasificación de INEGI.

| Macrosector | Sectores SCIAN | Establecimientos 05/2026 | Peso |
|---|---|---|---|
| Comercio | 43, 46 | 227 775 | 49.2 % |
| Alimentos y hospedaje | 72 | 58 167 | 12.6 % |
| Servicios personales y comunitarios | 81, 71 | 72 638 | 15.7 % |
| Salud, educación y gobierno | 62, 61, 93 | 37 441 | 8.1 % |
| Servicios profesionales y financieros | 51, 52, 53, 54, 55, 56 | 28 129 | 6.1 % |
| Industria y construcción | 31-33, 23, 21, 22 | 34 689 | 7.5 % |
| Transporte y campo | 48-49, 11 | 3 890 | 0.8 % |

- **Dónde vive la agrupación:** en las semillas `ref_macrosector` (los 7 macrosectores) y `ref_scian_sector` (columna `cve_macrosector`, un macrosector por sector). Para cambiarla basta editar los CSV y reconstruir; no hay que tocar el modelo.
- **Cómo se llega desde un establecimiento:** hecho → `dim_actividad` → `sk_macrosector`.
- **El color no está aquí.** Se define en el sistema visual; el modelo solo sabe qué sectores incluye cada macrosector.
- **Cosas que conviene recordar al interpretar:** Comercio es casi la mitad de CDMX, así que un mapa por macrosector será dominado por ese color. Salud, educación y gobierno junta lo público e institucional, que es donde el DENUE sobrerregistra frente al Censo (educación, 2.04 veces). Transporte y campo pesa menos del 1 %.

## 5. Pruebas

140 elementos (modelos, semillas y pruebas) en `dbt build`, todos en verde.

- **Llaves:** `unique` y `not_null` en la llave sustituta de cada dimensión; `unique` en las claves naturales.
- **Integridad referencial:** el hecho tiene `relationships` a cada dimensión; `dim_actividad` a sector; `dim_ageb` a alcaldía; `dim_ubicacion` a AGEB.
- **Valores válidos:** `metodo` de `vinculo_edicion` ∈ {id, difuso, id_salto, id_reusado, ninguno}; `metodo_colonia` ∈ {poligono, cercania, nombre, ninguna}; `alcaldia_colonia` ∈ {coincide, frontera, discrepante}; entidad = '09'.
- **`fact_conserva_filas_validas`:** por edición, el hecho debe tener exactamente las filas de origen menos las excluidas.
- **`establecimiento_una_version_por_edicion`:** ningún establecimiento cae en dos versiones en la misma edición.
- **`stg_denue_id_unico_por_edicion`:** el id DENUE no se repite dentro de una edición.
- **Conglomerados:** clave natural única y método de asignación válido (`campo` o `espacial`) en `dim_conglomerado`; el puente solo referencia conglomerados que existen. Un índice único garantiza un solo conglomerado principal por establecimiento y edición.
- **Macrosectores:** cada sector y cada actividad tiene macrosector (`not_null` y `relationships`).
- **Tramos:** `unique` y `not_null` en `sk_tramo`, y valores válidos de `metodo_tramo` en la asignación y en el hecho.
- **Censo:** `unique`/`not_null` en las llaves, valores válidos de nivel de actividad y de estrato, y el aviso `denue_cercano_al_censo`.

## 6. Decisiones y supuestos

| Tema | Decisión |
|---|---|
| Puntos fuera de CDMX | Excluidos en las cuatro ediciones; quedan en `registro_excluidos` |
| Modelo de datos | Completo, sin simplificar (decisión del proyecto) |
| Versión SCIAN | Se deduce de los códigos de clase, no del diccionario de INEGI (que dice 2018 en todas): 05/2024 es SCIAN 2018; desde 11/2024 es SCIAN 2023. `dim_actividad` tiene una fila por versión × clase |
| Atributos seguidos por el SCD2 | Id, nombre, razón social, tipo, contacto, edificio, piso y fecha de alta; el `clee` no |
| Reaparición | Un negocio que falta una o más ediciones y vuelve con el mismo id se vincula a su última aparición (`id_salto`) |
| Reconciliación difusa | Nombre normalizado + clase (o equivalente 2018/2023) + 30 m, uno a uno, contra la edición inmediata anterior |
| Colonia sin polígono | Por nombre parecido (≥ 0.5, misma alcaldía, ≤ 2 km); si no, miembro "sin colonia (<alcaldía>)" |
| Salto 11/2024 | Se marca con `comparable_con_anterior = false` en `dim_edicion`; no se corrige |
| Colonia | En el hecho, no en `dim_ubicacion`, porque una manzana contiene puntos de colonias distintas |
| Radio de mercados del padrón | 1.5 × √(superficie/π), por calibración |
| Conglomerado principal | Menor prioridad y menor superficie; tianguis y mercados sobre ruedas nunca |

## 7. Lo que hay que tener presente al usar los datos

- **Salto 05/2024 → 11/2024.** Hay 133 269 altas nuevas y 151 146 bajas entre estas dos ediciones. Coincide con la incorporación del Censo Económico 2024: casi todos los registros con alta en 2024 son ids nuevos. Las series que crucen esa frontera mezclan crecimiento real con cambio de fuente.
- **Edición 05/2025.** Contiene un registro con fecha de alta en 2026-01 aunque se publicó en mayo de 2025.
- **Cobertura de los conglomerados.** Solo el 22 % de los establecimientos tiene conglomerado principal, y 87 % de eso viene de lo que el DENUE declara. Los que el DENUE no clasifica quedan sin conglomerado aunque estén en una plaza. Los radios de mercados del padrón se calibraron; los de tianguis y OSM, no.
- **Llaves sustitutas no estables** entre reconstrucciones (ver 4.3). Cualquier tabla que las guarde fuera de dbt queda desalineada si se reconstruye `core`.

## 8. Pendiente

| Pendiente | Qué falta |
|---|---|
| Red peatonal | Banquetas y veredas de OpenStreetMap para "Islas de 15 minutos"; los tramos actuales son vehiculares y peatonales formales |
| Reconciliar conglomerados repetidos | Fusionar el mismo mercado o plaza que aparece en el campo del DENUE, el padrón y OSM |
| Corredores comerciales | Calles con alta densidad de comercio; se derivan de los tramos, no son un conglomerado de fuente externa |
| Organización jurídica | El DENUE no la trae |
| Redes sociales y "coordenada es centroide" | El DENUE no las trae; las banderas de contacto de hoy son web, correo y teléfono |
| Nombres SCIAN 2018 de subsector, rama y subrama | Hoy son los de SCIAN 2023 (catálogo del Censo). Para los 2018 exactos hay que exportar el catálogo en línea de INEGI |
| Censo 2019 | No cargado; permitiría comparar antes y después de la pandemia |

## 9. Cómo reconstruir

Detalle en [dbt/README.md](../dbt/README.md). Resumen:

```bash
ssh -f -N -L 55432:localhost:5433 vps
cd pipeline && set -a && . ../.env && set +a
uv run python cargar_raw.py <edicion> <csv> <publicacion>   # una vez por edición
uv run python cargar_externas.py
uv run python cargar_ce.py
uv run python cargar_osm_calles.py   # tras descargar_osm_calles.py
uv run dbt seed  --project-dir ../dbt --profiles-dir ../dbt
uv run dbt build --project-dir ../dbt --profiles-dir ../dbt
```

Tiempos aproximados (VPS de 32 GB): `vinculo_edicion` 48 s, `entidad_establecimiento` 15 s, `dim_establecimiento` 19 s, `asignacion_colonia` 31 s, `asignacion_tramo_punto` 3 min 20 s, `asignacion_tramo` 30 s, `fact_establecimiento` 1 min. Una construcción completa de `core` tarda unos 8 minutos.

## 10. Archivos

| Ruta | Contenido |
|---|---|
| `pipeline/cargar_raw.py` | Carga un CSV del DENUE a `raw.denue` (idempotente por edición) |
| `pipeline/cargar_externas.py` | Carga colonias, mercados, tianguis y mercados sobre ruedas a `raw` |
| `pipeline/cargar_osm_comercio.py` | Carga las áreas comerciales de OpenStreetMap a `raw.osm_comercio` |
| `dbt/models/staging/` | `stg_denue`, `stg_colonias`, `stg_mercados`, `stg_ce2024`, `stg_ce_catalogo_actividad`, `stg_ce_variable`, `stg_osm_calles`, `stg_tianguis`, `stg_mercados_sobre_ruedas`, `stg_osm_comercio` y fuentes |
| `dbt/models/core/` | Los 30 modelos de `core` y `_core.yml` con las pruebas |
| `pipeline/descargar_osm_calles.py`, `pipeline/cargar_osm_calles.py` | Descarga las calles de OpenStreetMap por mosaicos y las carga a `raw.osm_calles` |
| `pipeline/generar_vista_descargas.py` | Genera `docs/vista_contenido_descargado.html`, una vista de lo descargado |
| `pipeline/cargar_ce.py` | Carga el Censo Económico 2024 (CDMX), su diccionario y su catálogo de actividades a `raw` |
| `dbt/seeds/` | `ref_estrato`, `ref_scian_sector`, `ref_macrosector`, `ref_scian_2023_2018` |
| `dbt/tests/` | Las 3 pruebas singulares |
| `dbt/macros/` | `generate_schema_name` (esquemas sin prefijo) y `clave_ubicacion` |
| `data/raw/MANIFEST.md` | Origen, fechas y hashes de las descargas |

# Pulso DENUE CDMX — Síntesis del proyecto

Nov 8, 2026 · @Ricardo MMD · Revisión 3

## Cómo usar este documento

Pulso DENUE CDMX está en fase de concepto y diseño: hay decisiones cerradas de alcance, escenas, stack, contrato de escena, persistencia de paneles y coreografía, y todavía no hay código. Este documento resume todo lo acordado para retomar el trabajo en otro chat o en Claude Code sin perder contexto.

**Para retomar en otro chat:** pega este documento y pide continuar desde "Próximos pasos".

**Para Claude Code:** guárdalo en el repositorio (por ejemplo, `docs/concepto.md`). Las secciones de vocabulario, contrato de escena, persistencia, recorridos y coreografía funcionan como especificación.

**Ajustes al contrato de escena (14 nov 2026, spec de H09 aceptada)**

El detalle está en `docs/changes/2026-11-08-contrato-escena/spec.md`. Cambia cuatro puntos de la sección "Contrato del estado de escena":

- El origen y el panel anterior salen del estado y pasan a ser metadatos, para que el mismo panel tenga el mismo id venga de donde venga.
- La validación tiene tres niveles. El de dispositivo deja de ser validación: cada escena declara su agregado para celular y el motor lo aplica.
- En Corredores del Metro la línea es el territorio, no un parámetro, y el ranking admite toda la ciudad.
- En Corredores del Metro la selección por giro solo atenúa puntos; sus cifras no cambian con el giro.

**Cambios en la revisión 3 (8 nov 2026)**

- Se actualiza el estado real: la capa `semantic` tiene 18 tablas con `lugar` (ver "Próximos pasos"); ya existen las de Metro, Colonias gemelas y Cómo se llaman las cosas, además de `censo_sector` y `cobertura_censo`.
- Se unifica la numeración de prototipos: 1 = cobertura de campos y compuerta de conglomerados, 2 = renderizador, 3 = resolver lugar.
- Se corrige la fuente del Metro: estaciones y líneas vienen de OpenStreetMap (`pipeline/cargar_osm_metro.py`); no se carga GTFS.
- Se añade "Estado de avance" con lo hecho, lo pendiente y los desfases conocidos.

**Cambios en la revisión 2**

- Se retiran las restricciones de privacidad: el portal muestra establecimientos individuales con nombre.
- Coreografía recalculada: la transición estándar cabe en 1.5 s y las excepciones tienen tope declarado.
- Vocabulario único para escena, modo, recorrido, panel e historia; "Centro contra periferia" se apoya en la escena nueva "Anillos de densidad".
- Se especifican la persistencia de paneles compartidos, el flujo de cifras, la fuente única del contrato, las reglas de herencia, los límites del Analista y la zona caminable del Metro.
- Modelo de datos ampliado: dimensiones de conglomerado y tramo de calle, reconciliación entre ediciones y capas de esquema.
- Propuestas para los riesgos de cobertura del campo conglomerado, del costo de la alternativa 2D y de la dependencia de Theatre.js.

**Decisiones cerradas**

- Nombre: Pulso DENUE CDMX.
- Alcance: solo Ciudad de México.
- Narrativa por paneles, no por scroll.
- Dos factores de innovación: escenas animadas con Three.js y un agente analista con Claude (RAG + text-to-SQL).
- El Analista mueve la escena generando paneles.
- H3 se omite en la primera etapa; se trabaja con unidades oficiales (alcaldía, colonia, AGEB, manzana).
- Escenas: la ciudad de luz (neutra) más 10 escenas temáticas; 2 historias conservadas.
- Un solo renderizador Three.js, sin mapa base de terceros.
- Sin restricciones de privacidad adicionales: el DENUE es información pública y se muestra a nivel establecimiento, con nombre.
- Modelo de datos completo (estrella con copos de nieve, multi-edición y SCD tipo 2) desde el inicio.

**Pendiente de decidir:** sistema visual (paleta, tipografía, tratamiento de luz), guion completo de las historias, edición anterior para comparar (la base ya está fijada: DENUE 05/2026) y resultados de los prototipos de validación.

## Concepto

**Tesis:** la animación es la forma de mostrar el dato, no un adorno encima del dato. La Ciudad de México contada a través de sus negocios, establecimiento por establecimiento.

**Producto:** un portal para explorar el DENUE de CDMX con dos factores de innovación:

1. **Escenas animadas (motion graphics con Three.js)** en lugar de gráficos tradicionales, para generar impacto, atracción y comprensión estadística de calidad.
2. **El Analista:** un agente LLM que funciona como analista senior experto en DENUE, responde con datos reales y genera paneles que mueven la escena. Estrategia RAG + text-to-SQL con la API de Claude.

**Reglas de diseño**

1. **Cada escena responde una pregunta.** Si no se puede escribir en una línea, la escena sobra.
2. **Toda escena tiene una vista exacta:** cifra, tabla equivalente y fecha de corte, siempre accesibles.
3. **Continuidad visual:** los mismos puntos viajan entre vistas; un establecimiento del mapa es el mismo que luego forma una barra. En celular la continuidad es por unidad territorial: el agregado de una AGEB o colonia es el que viaja.
4. **Cada panel es un estado compartible:** cualquier hallazgo, incluido uno del Analista, tiene su propio enlace.

**Edición base: DENUE 05/2026** (publicada el 20 de mayo de 2026; la siguiente, el 25 de noviembre de 2026). **Escala de CDMX:** 462 732 establecimientos, todos con coordenadas y sin ids duplicados. Iztapalapa concentra 19,1 %, Cuauhtémoc 14,6 % y Gustavo A. Madero 11,0 %. El 29 % de los registros (133 241) tiene fecha de alta en 2024, el año del Censo Económico. A esta escala se pueden mostrar todos los puntos en tiempo real en escritorio.

## Vocabulario

Términos con significado fijo en todo el proyecto, en el código y en el contrato.

| Término | Definición | Ejemplo |
| --- | --- | --- |
| Escena | Modo del motor con su pregunta, parámetros y codificaciones permitidas | Corredores del Metro |
| Modo | Variante de forma dentro de una escena; puede ser geográfica o abstracta | Corredores del Metro en modo ranking de estaciones |
| Recorrido | Movimiento de cámara y de puntos sobre una escena, dividido en tiempos | Tren de luz |
| Tiempo | Subdivisión de un recorrido que el usuario avanza como panel interno | Tiempo 2 del Tren de luz |
| Panel | Un estado de escena validado, con dirección propia | `/p/7Gk2mQx9aZ` |
| Historia | Secuencia editorial de 5 a 8 paneles | Vida comercial del Metro |
| Secuencia del Analista | Paneles generados en una conversación, en orden | `/c/{id}` |

**Forma geográfica:** cada punto ocupa su posición en la ciudad. **Forma abstracta:** los puntos abandonan su posición para formar otra figura (interior de un conglomerado, hélice, ranking, perfil).

## Conocimiento base del DENUE

El DENUE es un directorio de establecimientos con ubicación, no un censo: la unidad es el establecimiento, no la empresa, y cada edición tiene una fecha de corte que debe citarse siempre.

**Campos principales**

- Identificador del establecimiento, nombre comercial y razón social.
- Actividad económica: código SCIAN de 6 dígitos (sector 2, subsector 3, rama 4, subrama 5, clase 6).
- Estrato de personal ocupado (rangos, no conteos exactos).
- Dirección desglosada y coordenadas.
- Claves geográficas: entidad, municipio (alcaldía), localidad, AGEB y manzana.

**Campos olvidados (base de las escenas innovadoras)**

| Campo | Escena que habilita |
| --- | --- |
| Conglomerado: tipo y nombre (mercado público, centro comercial, corredor) y número de local | Ciudades dentro de la ciudad |
| Correo, sitio web, Facebook, Twitter | La ciudad que brilla en línea |
| Nombre de vialidad y entre calles | Las calles hablan |
| Nombre comercial | Cómo se llaman las cosas; etiquetas de Rarezas |
| Fecha de alta (incorporación al DENUE, no apertura) | Descartada por ahora; se conserva en el modelo |
| Piso o nivel del edificio | Descartada por ahora; se conserva en el modelo |
| Tipo de establecimiento (fijo o semifijo) | Filtro disponible |
| Organización jurídica (persona física o moral) | Filtro disponible |

Muchos de estos campos vienen incompletos. Hay que medir su cobertura en CDMX antes de construir cada escena (prototipo 1).

**Trampas de calidad**

- Versiones SCIAN (2013, 2018, etc.): las series se rompen entre versiones.
- Coordenadas de calidad variable; algunas son centroides.
- Duplicados, rezago en bajas e identificadores que pueden cambiar entre ediciones.
- El campo de colonia es texto inconsistente: la colonia se asigna espacialmente.
- Cobertura parcial del comercio en vía pública y del sector informal sin ubicación fija.
- Establecimiento no es empresa: matriz y sucursales son registros distintos.

**Uso de los datos:** el DENUE es público; el portal muestra registros individuales, incluido el nombre comercial, y siempre cita la fuente (INEGI, DENUE) y la fecha de corte.

**Validación externa:** Censos Económicos 2024 (CDMX: 454 mil establecimientos) como referencia para contrastar conteos.

## Modelo de datos

Esquema estrella con grano de un establecimiento por edición del DENUE. Las dimensiones de actividad y geografía se normalizan en copo de nieve porque son las que cambian entre versiones y se recorren por jerarquía.

**Capas de esquema en PostgreSQL**

| Esquema | Contenido | Quién lo usa |
| --- | --- | --- |
| `raw` | Cargas tal como vienen de cada fuente, con fecha de carga | Pipeline |
| `staging` | Tipos corregidos, claves limpias, geometrías válidas | dbt |
| `core` | Hechos, dimensiones y tablas de apoyo | dbt, exportación del paquete estático |
| `semantic` | Vistas semánticas documentadas; única superficie del Analista | Analista, vista exacta, paquete estático |
| `app` | Paneles, conversaciones, registro de consultas y caché | Backend |

**Tabla de hechos: FACT\_ESTABLECIMIENTO**

- Llaves sustitutas a cada dimensión: sk\_edicion, sk\_ubicacion, sk\_actividad, sk\_estrato, sk\_establecimiento, sk\_conglomerado, sk\_tramo.
- Medidas: cantidad (siempre 1, para contar), longitud, latitud, geometría (geography en PostGIS), x e y en la proyección local (metros, UTM 14 norte con origen en el centro de la ciudad).
- Banderas derivadas: tiene web, correo, redes; coordenada es centroide; colonia asignada por cercanía.

**Dimensiones**

| Dimensión | Contenido | Nota |
| --- | --- | --- |
| DIM\_EDICION | Año, fecha de corte, versión SCIAN, fecha de carga | Evita mezclar versiones de clasificación |
| DIM\_UBICACION | Claves de entidad a manzana, código postal, colonia | Colonia asignada espacialmente |
| DIM\_ACTIVIDAD | Código SCIAN de clase, nombres de clase y sector, macrosector del portal | Copo de nieve hasta sector |
| DIM\_ESTRATO | Etiqueta, límite inferior y superior, punto medio | Pequeña y estable |
| DIM\_ESTABLECIMIENTO | id DENUE, nombre, razón social, tipo, organización jurídica, contacto, piso, fecha de alta | SCD tipo 2 (vigente desde, vigente hasta, edición de alta y de baja) |
| DIM\_CONGLOMERADO | Tipo, nombre normalizado, polígono o radio, origen (campo DENUE o asignación espacial) | Habilita Ciudades dentro de la ciudad |
| DIM\_TRAMO | Tramo de calle asignado, nombre de vialidad normalizado, colonia, método de asignación | Habilita Las calles hablan |

**Variante copo de nieve**

- Geografía: manzana → AGEB → localidad → alcaldía → entidad; colonia como jerarquía paralela (colonia → alcaldía).
- SCIAN: clase → subrama → rama → subsector → sector → macrosector del portal.
- Tabla de correspondencia SCIAN entre versiones (2013 ↔ 2018 ↔ siguientes) para comparar ediciones a nivel de rama o superior.

**Llaves:** enteros sustitutos para joins; las claves naturales de INEGI (id DENUE, claves geográficas) se conservan como atributos para reconciliar cargas.

**Reconciliación entre ediciones (alimenta el SCD tipo 2)**

1. Coincidencia por id DENUE.
2. Si el id no coincide: nombre normalizado + clase SCIAN + distancia menor a 30 m.
3. Si no hay coincidencia: alta nueva; los registros de la edición anterior sin pareja se cierran como baja.
4. Cada vínculo guarda el método (id, difuso, ninguno) para auditar la serie.

**Asignación de colonia:** punto en polígono contra el catálogo de colonias de datos abiertos CDMX; si el punto cae fuera de todo polígono, colonia más cercana a menos de 50 m; si no, "sin colonia". El método queda en la bandera correspondiente.

**Tablas de apoyo para las escenas:** colonias (polígonos de datos abiertos CDMX), estaciones, accesos y líneas de transporte, tramos de calle, población por AGEB y manzana, polígonos de conglomerados (padrón de mercados públicos, OSM), perfiles sectoriales por colonia (vectores para similitud en pgvector) y accesibilidad a pie por manzana.

**Tablas de aplicación (`app`):** panel, conversación, consulta (registro de SQL, filas, tiempo y costo) y caché de intención. Ver "Persistencia de paneles".

## Experiencia por paneles

La narrativa avanza por paneles (botón, flecha o gesto de deslizar), no por scroll. Los paneles hacen posible que el Analista mueva la escena: cada panel es un estado discreto, y la respuesta del Analista es un panel nuevo.

**Secciones del portal**

- **Historias:** secuencias editoriales de 5 a 8 paneles con indicador de posición y salida a "explorar desde aquí".
- **Explorador:** escena libre con filtros; cualquier vista se puede fijar como panel.
- **El Analista:** cada respuesta genera un panel que se suma a la secuencia de la conversación.
- **Fichas:** por alcaldía y por sector.
- **Metodología y datos:** cobertura, versiones, fecha de corte, límites y descargas.

**Por qué paneles y no scroll:** con scroll el estado depende de la posición de la página y entra en conflicto con el Analista. Con paneles, la historia editorial y la respuesta del Analista usan el mismo contrato de estado: el usuario puede volver atrás, comparar o compartir cualquier panel.

**Accesibilidad:** cada escena tiene alternativa 2D construida con los componentes genéricos de la vista exacta (ver "Propuestas para los riesgos de la primera versión") y respeta la preferencia de movimiento reducido del sistema.

## Escenas e historias

La ciudad de luz es la escena neutra de inicio y de paso entre escenas; hay 10 escenas temáticas y 2 historias conservadas.

| Escena | Pregunta | Campo o cruce | Metáfora | Cuidado |
| --- | --- | --- | --- | --- |
| Ciudad de luz (neutra) | ¿Dónde vive la economía de la ciudad? | Ubicación, SCIAN | Todos los establecimientos como puntos sobre una CDMX oscura | — |
| Ciudades dentro de la ciudad | ¿Cuánta economía cabe en un mercado, plaza o central? | Conglomerado, número de local | Cada conglomerado es una esfera de partículas que se abre en pasillos por giro | Compuerta de cobertura (prototipo 1) |
| La ciudad que brilla en línea | ¿Qué negocios declaran presencia digital y dónde? | Web, correo, redes | Halo en negocios con presencia digital; brecha por alcaldía | Mide presencia declarada, no real |
| Las calles hablan | ¿Qué calles se especializan en algo? | Vialidad + SCIAN, red vial | Calles con grosor por densidad y color por giro dominante | Asignación por nombre y cercanía |
| Islas de 15 minutos | ¿Desde dónde se resuelve la vida diaria caminando? | Red peatonal OSM, población | Las zonas completas emergen del agua como islas | Categorías esenciales fijas |
| Corredores del Metro | ¿Qué vida comercial tiene cada línea? | Estaciones y líneas (OpenStreetMap) | Tren de luz que enciende negocios estación por estación | Zona caminable definida abajo |
| El ADN de cada alcaldía | ¿Qué hace única a cada alcaldía? | Cociente de localización | Hélice con segmentos por sector; se transforma al comparar | — |
| Colonias gemelas | ¿Qué colonia se parece a la mía? | Perfil sectorial, similitud coseno | Arcos de luz entre colonias gemelas | Explicar por qué se parecen |
| Rarezas | ¿Qué negocios son únicos en su territorio? | Conteo de clases SCIAN | Apagón general; queda una constelación de lo raro, con el nombre de cada negocio | — |
| Cómo se llaman las cosas | ¿Cómo nombra la ciudad a sus negocios? | Nombre comercial tokenizado | Palabras flotantes sobre las zonas donde predominan | Frecuencia mínima para evitar ruido |
| Anillos de densidad | ¿Cómo cambia la economía del centro hacia afuera? | Distancia al Zócalo, densidad, diversidad | Anillos concéntricos que laten por densidad y mezcla | Densidad normalizada por superficie |

**Modos por escena**

| Escena | Modos geográficos | Modos abstractos |
| --- | --- | --- |
| Ciudades dentro de la ciudad | Exterior (esferas sobre el mapa) | Interior (pasillos por giro) |
| Corredores del Metro | Línea | Ranking de estaciones |
| El ADN de cada alcaldía | — | Hélice |
| Colonias gemelas | Arcos | Perfiles superpuestos |
| Anillos de densidad | Anillos | Perfil de densidad |
| Las demás | Única | — |

**Zona caminable del Metro**

- Primera versión: radio euclidiano alrededor de cada estación; valores permitidos de 300, 500 (predeterminado) y 800 m.
- Cada establecimiento se asigna a la estación más cercana dentro del radio, para no contarlo dos veces en rankings; la vista de línea usa la unión de radios.
- Segunda etapa: distancia de red peatonal de 5 y 10 minutos, con la misma red de Islas de 15 minutos.
- Alcance: Metro. Metrobús y Tren Ligero quedan para después con el mismo mecanismo.

**Historias conservadas**

- **Vida comercial del Metro:** qué estaciones concentran más negocios y de qué tipo. Usa Corredores del Metro en modos línea y ranking.
- **Centro contra periferia:** densidad y mezcla de giros del centro hacia las alcaldías del oriente y el sur. Usa Anillos de densidad.

**Otras historias propuestas (sin confirmar):** la ciudad de los micronegocios, la geografía de la tiendita, qué tan lejos queda la farmacia, vocación de cada alcaldía.

**Escenas descartadas:** la ciudad vertical (piso), lo fijo y lo que se mueve, sedimentos de la ciudad (fecha de alta), personas y empresas, monocultivo y mezcla, la ciudad que suena.

## Stack y pipeline

La complejidad está en el cálculo previo, no en el navegador: el frontend anima resultados ya calculados y la base de datos responde lo dinámico (el Analista y búsquedas puntuales).

| Capa | Elección | Razón |
| --- | --- | --- |
| Interfaz | Vue 3 + Vite | Continuidad con el Asistente INEGI |
| Motor 3D | Three.js directo (no TresJS) | Shaders propios y partículas persistentes |
| Mapa | Sin mapa base; fondo propio dibujado desde datos | Control estético y un solo contexto WebGL |
| Estado | Pinia + esquema validado del estado de escena | Mismo esquema valida historias y Analista |
| Transiciones | GSAP | Interpolación entre estados y reproducción de recorridos |
| Recorridos de autor | Theatre.js como editor; formato propio en ejecución | Diseño visual sin depender de Theatre.js en producción |
| Postprocesado | postprocessing (pmndrs) | Brillo y halos |
| Texto 3D | troika-three-text | Miles de etiquetas legibles |
| Backend | FastAPI + Pydantic v2 | Analista, consultas dinámicas, validación, fuente del contrato |
| Base de datos | PostgreSQL 18 + PostGIS + pgvector (pgRouting opcional), en un clúster propio del VPS actual | Datos, geometría y RAG en un solo lugar; aislado de las demás bases |
| Modelado | dbt sobre PostgreSQL | Transformaciones versionadas y documentadas |
| Procesamiento | Python, Polars, DuckDB espacial | Limpieza, tokenización, perfiles |
| Accesibilidad a pie | Pandana o r5py sobre red OSM | Distancias de red masivas en minutos |
| Infraestructura | Docker + Traefik en VPS; CDN para estáticos | Stack actual; el tráfico pesado no pasa por el VPS |

**Decisiones técnicas clave**

- **Un lienzo persistente:** el canvas no se destruye al cambiar de panel; los paneles solo cambian estado. Es la base de la continuidad visual.
- **Proyección local:** coordenadas en metros (UTM 14 norte) con origen en el centro de la ciudad, para evitar temblores por precisión numérica en WebGL.
- **WebGL2 como base;** WebGPU como mejora futura.
- **Sin H3 en la primera etapa:** cálculos sobre manzana y AGEB, normalizando por superficie; la versión celular agrega por AGEB o colonia.

**Base en el VPS**

- Instancia: clúster PostgreSQL 18 nativo (repositorio PGDG) en `localhost:5433` del VPS (32 GB de RAM, disco con holgura), con su propia configuración de memoria. Convive con el clúster 16 (puerto 5432: `electoral_mx`, `inegi_ine_db` y otras), cuyo PostGIS se actualizó a 3.7.0 al instalar el 18; los PostgreSQL en contenedores son de n8n y no se usan. Implementado el 2026-11-02. Guía de instalación en `db/INSTALAR_POSTGRES18.md`.
- Base `pulso_denue` con tres roles: `pulso_owner` (dbt y pipeline), `pulso_app` (backend) y `pulso_analista` (solo lectura de `semantic`, 8 s por consulta, 10 conexiones). Arranque en `db/00_bootstrap.sql`.
- Acceso desde desarrollo por túnel SSH; el puerto 5433 no se abre a internet. El backend en Docker llega a la base por la red del host, como el bot electoral.
- Las credenciales viven en `.env` (no versionado) y en un gestor de contraseñas; nunca en el repositorio ni en documentos.
- Respaldo diario con `pg_dump` y retención de 7 días; los parámetros de memoria del clúster (`shared_buffers` 4 GB, `work_mem` 64 MB) vienen en la guía de instalación.

**Fuentes de datos**

- DENUE CDMX (descarga masiva por edición).
- Marco Geoestadístico INEGI: alcaldías, AGEB, manzanas, vialidades.
- Censo 2020: población por AGEB y manzana.
- Datos abiertos CDMX: polígonos de colonias, estaciones de transporte y padrón de mercados públicos.
- OpenStreetMap: red peatonal, calles, estaciones y líneas del Metro, mercados y centros comerciales.
- GTFS de CDMX: no se carga por ahora; solo se necesitaría si se agregan Metrobús o Tren Ligero.

**Productos del pipeline por edición**

1. **Paquete estático para el navegador (CDN):**
   - Puntos en binario compacto: x e y cuantizados a 1 m en Uint16 sobre el rectángulo de CDMX, índice de clase SCIAN (Uint16), estrato (Uint8), alcaldía (Uint8), colonia y AGEB (Uint16), banderas en bits.
   - Agregados por unidad oficial y geometrías simplificadas para el fondo y la alternativa 2D.
   - Resultados precalculados de historias y fichas, uno por archivo, nombrados por el hash de vista + parámetros + edición.
   - Catálogo de referencias válidas (ids de territorios, clases SCIAN, conglomerados, estaciones) para validar en el navegador.
2. **Base para el Analista:** esquema estrella con vistas semánticas.

**Flujo de cifras: dónde se calcula cada número**

| Origen del panel | Dónde se calculan las cifras | Necesita backend |
| --- | --- | --- |
| Historias y fichas | Pipeline, ejecutando las mismas vistas semánticas; viajan en el paquete estático | No |
| Explorador | Navegador, en un web worker sobre los atributos del paquete (conteos por selección y territorio) | Solo para búsquedas por nombre |
| Analista | Base de datos, vía vistas semánticas | Sí |

**Prueba de paridad:** en cada carga, el pipeline compara una muestra de cifras del paquete estático y del conteo en el navegador contra las vistas semánticas; cualquier diferencia detiene la publicación.

**Asignación a calles:** combina nombre de vialidad del DENUE con el tramo más cercano; ninguno de los dos funciona solo. El resultado se guarda en DIM\_TRAMO con su método.

**Presupuesto de rendimiento:** 60 cuadros por segundo con todos los puntos en escritorio; en celular, agregados y menos postprocesado. Cada escena se prueba en un celular de gama media.

## El Analista

El Analista es un analista senior experto en DENUE que nunca inventa cifras: cita la fecha de corte, dice qué no cubre el DENUE y responde con texto más un panel que mueve la escena.

**Flujo de una pregunta**

1. Clasifica: metodológica (RAG), cuantitativa (text-to-SQL) o mixta.
2. Resuelve el lugar y traduce el giro a SCIAN.
3. Busca en la caché de intención; si hay coincidencia, reutiliza el panel.
4. Consulta vistas semánticas, nunca tablas crudas.
5. Valida el resultado (cifras implausibles, versión SCIAN, territorio).
6. Responde con cifra, contexto, fecha de corte, consulta usada y estado de escena.

**Herramientas**

| Herramienta | Función |
| --- | --- |
| Resolver lugar | Convierte "la Roma", "cerca del metro Balderas" o "Iztapalapa" en identificadores territoriales. La más crítica |
| Traducir giro | Lenguaje común a clases SCIAN, con búsqueda semántica y glosario propio de CDMX ("tiendita", "fonda", "estética") |
| Consultar datos | Text-to-SQL sobre vistas semánticas |
| Buscar metodología | RAG sobre notas metodológicas, SCIAN y documentación de indicadores |
| Construir escena | Devuelve un estado de escena que el backend valida |

**Modelos y servicios**

- Modelo ligero (Haiku) para clasificar, resolver lugares y traducir giros.
- Modelo capaz (Sonnet) para SQL, interpretación y redacción.
- Caché de prompt para esquema de vistas, glosario y catálogo SCIAN.
- Embeddings: la API de Claude no los genera; usar Voyage AI o un modelo multilingüe local.
- Orquestación: ciclo de uso de herramientas de la API de Claude; LangGraph solo si el flujo se ramifica.
- Observabilidad: Langfuse autoalojado (preguntas, herramientas, SQL, costo).
- Evaluación: banco de preguntas sobre CDMX con respuestas verificadas a mano, ejecutado en cada cambio.

**Seguridad de la base**

- Rol de solo lectura con acceso únicamente al esquema `semantic`, tiempo máximo por consulta y límite de filas.
- Análisis del SQL generado antes de ejecutarlo (sqlglot) para permitir solo vistas autorizadas.
- Listados de establecimientos limitados a 200 filas en la respuesta; el listado completo se descarga desde la vista exacta.
- Responde "el DENUE no puede responder eso" cuando excede la cobertura y sugiere otra fuente.

**Límites de uso del Analista público**

| Nivel | Límite inicial (configurable) | Al alcanzarlo |
| --- | --- | --- |
| Acceso | Verificación anti-bots (Cloudflare Turnstile) en la primera pregunta de cada sesión | — |
| Por IP | 10 preguntas cada 10 minutos y 60 al día; primera barrera en el middleware de Traefik | Mensaje con hora de reapertura |
| Por conversación | 40 turnos; el contexto anterior se resume | Ofrece abrir conversación nueva |
| Por pregunta | 6 llamadas a herramientas, 2 reintentos de SQL, tope de tokens de salida | Responde con texto y vista exacta |
| Concurrencia | 8 preguntas en paralelo; cola corta | Indicador de espera |
| Presupuesto | Tope diario y mensual en dólares, medido con el uso real de tokens; alerta al 80 % | Modo degradado: solo caché y Explorador, con aviso visible |

**Caché de intención:** la clave no es el texto de la pregunta sino la intención resuelta por el modelo ligero: edición, tipo de pregunta, ids de lugar, clases SCIAN, métrica y escena. "¿Cuántas fondas hay en la Roma?" y "número de fondas en la colonia Roma" comparten panel. La respuesta en caché reutiliza el panel guardado y su redacción; se invalida al cambiar de edición.

## Contrato del estado de escena

El estado de escena es el contrato central: lo escriben las historias, el explorador y el Analista, y lo interpreta un solo motor.

**Principios**

1. Declarativo: describe qué se ve, no cómo se anima.
2. Referencias, no datos: identificadores, nunca coordenadas ni listas de puntos.
3. Cerrado: valores permitidos por campo; lo demás se rechaza.
4. Parcial y heredable: un estado nuevo puede cambiar un solo elemento y hereda el resto (reglas abajo).
5. Determinista: mismo estado y edición producen la misma imagen y cifras.
6. Las cifras se vinculan, no se escriben: vienen de una consulta ejecutada.

**Anatomía**

| Bloque | Contenido |
| --- | --- |
| Identidad | Versión del contrato y edición DENUE. El origen (historia, explorador, Analista) y el panel anterior son metadatos del panel, fuera del estado |
| Territorio y encuadre | Ciudad, alcaldía, colonia, AGEB, manzana, estación, calle, conglomerado o punto con radio. Modos: ajustar al territorio, vista con ángulo (cenital, oblicua, rasante) o recorrido de autor |
| Escena | Tipo de escena, modo y sus parámetros |
| Selección | Giro SCIAN, estrato, tipo de establecimiento, organización jurídica, conglomerado, presencia digital. Filtrar atenúa, nunca elimina puntos |
| Codificación visual | Color y tamaño, solo entre las opciones permitidas por escena |
| Capas de contexto | Siluetas de alcaldías, líneas de Metro, calles principales, etiquetas |
| Comparación | Segundo territorio o selección: lado a lado o transformación |
| Narrativa | Título, texto con huecos para cifras vinculadas, cifra principal con unidad y denominador, hasta tres secundarias, nota de cautela, fuente y fecha de corte |
| Vista exacta | Referencia a la vista semántica, parámetros y tipo de resultado (ranking, territorial, comparación, perfil, serie), que decide la tabla y el gráfico 2D |
| Interacción | Cursor para detalle (registro completo con nombre), explorar desde aquí, guardar, compartir; exploración bloqueable en historias |

**Parámetros por escena**

| Escena | Territorio mínimo | Parámetros | Codificaciones |
| --- | --- | --- | --- |
| Ciudad de luz | Ciudad | Ninguno | Macrosector |
| Ciudades dentro de la ciudad | Alcaldía o conglomerado | Tipo de conglomerado; modo exterior o interior | Giro; tamaño por locales |
| La ciudad que brilla en línea | Ciudad | Tipo de presencia (web, correo, redes, cualquiera) | Presencia digital |
| Las calles hablan | Alcaldía o colonia | Mínimo de negocios por calle | Giro dominante, densidad |
| Islas de 15 minutos | Alcaldía o ciudad | Distancia: 10, 15 o 20 minutos; categorías fijas | Categorías alcanzables |
| Corredores del Metro | Línea o estación; ciudad en modo ranking | Modo línea o ranking; distancia caminable 300, 500 u 800 m | Giro, conteo por estación |
| ADN de alcaldía | Alcaldía | Base: ciudad u otra alcaldía | Cociente de localización |
| Colonias gemelas | Colonia | Número de gemelas (1 a 5); modo arcos o perfiles | Similitud |
| Rarezas | Alcaldía o ciudad | Umbral: únicas o hasta 3; etiquetas con nombre sí o no | Giro |
| Cómo se llaman las cosas | Alcaldía o colonia | Tipo de palabra (todas, diminutivos, nombres propios) | Frecuencia |
| Anillos de densidad | Ciudad | Número de bandas; eje (todas, oriente, sur); modo anillos o perfil | Densidad, diversidad |

**Fuente única del esquema**

- El contrato se define en modelos Pydantic v2 en el backend (`contracts/escena.py`), incluido el catálogo de valores permitidos por escena.
- Se exporta a JSON Schema versionado (`contracts/escena.v{N}.json`) en cada cambio.
- Del JSON Schema se generan los tipos de TypeScript del frontend y el validador estructural del navegador (Ajv).
- Las historias se escriben como archivos JSON o YAML y se validan contra el esquema en integración continua.
- Cada cambio incompatible sube la versión del contrato y trae una función de migración de la versión anterior, para que los paneles guardados sigan abriendo.

**Reglas de herencia (principio 4)**

| Caso | Regla |
| --- | --- |
| Campos de un bloque | Se fusionan campo por campo; lo no mencionado se hereda |
| Listas (capas, secundarias) | Se reemplazan completas, nunca se mezclan |
| `null` explícito | Borra el campo y regresa al valor predeterminado de la escena |
| Cambio de tipo de escena | Se reinician parámetros, modo y codificación a los predeterminados de la nueva escena; se conservan territorio, selección y capas |
| Narrativa | Se hereda como plantilla y sus cifras se vuelven a vincular |
| Vista exacta | Se recalcula siempre |

**Validación en tres niveles**

1. Estructura: campos y valores permitidos.
2. Referencias: los identificadores existen en la edición.
3. Coherencia: la combinación tiene sentido (rarezas no admite manzana; gemelas exige colonia).

El dispositivo no es un nivel de validación: en celular el motor sustituye puntos por el agregado que declara cada escena, sin cambiar el estado.

El navegador valida los niveles 1 y 2 con el esquema y el catálogo de referencias del paquete estático; el backend valida los tres.

**Lo que el Analista puede y no puede hacer**

- Puede: elegir territorio, escena, modo, selección, comparación y capas; escribir título y texto con huecos; elegir un recorrido de autor existente; proponer estados parciales.
- No puede: escribir cifras, definir colores, escalas, coordenadas de cámara o recorridos nuevos, ni omitir la nota de cautela.
- Si falla la validación: corrige y reintenta; tras dos fallos responde solo con texto y vista exacta.

**Ejemplo:** "¿Qué mercados de Iztapalapa tienen más locales de comida?" → territorio Iztapalapa; escena ciudades dentro de la ciudad, modo exterior; selección mercado público + servicios de preparación de alimentos y bebidas; tamaño por locales de comida; narrativa con el mercado líder y su conteo vinculados; nota sobre cómo se registran locales en conglomerados. "¿Y en Cuauhtémoc?" solo cambia el territorio; la narrativa se hereda y sus cifras se vuelven a vincular.

## Persistencia de paneles

Cada panel tiene una dirección estable. El tipo de dirección depende de su origen.

| Origen | Dirección | Dónde vive |
| --- | --- | --- |
| Historia | `/historias/{slug}/{n}` | Paquete estático |
| Explorador | `/explorar#s={estado}`: JSON canónico comprimido en base64url; si pasa de 2 KB se guarda y usa `/p/{id}` | En la URL o en `app.panel` |
| Analista | `/p/{id}` | `app.panel` |
| Conversación del Analista | `/c/{id}`: la secuencia completa de paneles | `app.conversacion` |

**Identificador por contenido:** `id` son los primeros 10 caracteres en base62 del SHA-256 del estado canónico (claves ordenadas, sin campos predeterminados) más la edición. Dos paneles idénticos comparten id; guardar es idempotente.

**Tabla `app.panel`:** id, estado, edición, versión del contrato, origen, panel anterior, conversación, consulta SQL ejecutada, resultados congelados (cifras y tabla de la vista exacta, hasta 5 000 filas), fecha de creación. Se conserva indefinidamente; cada registro pesa pocos kilobytes.

**Paneles de ediciones anteriores:** un enlace abre siempre con su edición y sus resultados congelados, así que nunca cambia en silencio. Si hay una edición más reciente, aparece un aviso con "Ver con datos de {fecha de corte}", que vuelve a ejecutar la vista exacta con la nueva edición; es posible porque el estado solo guarda referencias. Si alguna referencia ya no existe en la nueva edición, el aviso lo dice.

## Recorridos de autor

Los recorridos se definen como plantillas relativas a su territorio, para que un solo diseño sirva para cualquier línea, calle, mercado o par de colonias. Cada recorrido se divide en tiempos que el usuario avanza como paneles internos.

- **Fijos:** únicos, para momentos editoriales; solo los usan las historias.
- **Plantillas:** parametrizables por territorio; los usan historias y Analista.

| Recorrido | Tipo | Escena | Duración | Tiempo 1 | Tiempo 2 | Tiempo 3 |
| --- | --- | --- | --- | --- | --- | --- |
| El despertar | Fijo | Ciudad de luz | 12–15 s | Negro; aparece la fecha de corte | Oleadas de encendido desde el Zócalo; cámara cenital | Descenso a vista oblicua; total cuenta hasta su valor |
| Tren de luz | Plantilla (línea) | Corredores del Metro, modo línea | 10–20 s | Ciudad atenuada; solo el trazo | Pulso recorre la línea y enciende negocios por estación; cámara rasante adelantada | Cámara sube; estación líder y giro dominante |
| Constelación de estaciones | Plantilla (ranking) | Corredores del Metro, modo ranking | 8–12 s | Estaciones como esferas por tamaño | Visita a las 5 mayores, de menor a mayor | Las esferas se ordenan en ranking |
| Del centro hacia afuera | Plantilla (eje) | Anillos de densidad | 10–14 s | Cámara cerca del Zócalo | Desplazamiento al oriente o sur con anillos de distancia | Anillos se vuelven perfil de densidad |
| Vuelo de calle | Plantilla (calle) | Las calles hablan | 6–10 s | Calle iluminada; demás apagadas | Vuelo rasante a altura de tres pisos | Cámara sube; calle en su colonia |
| Entrar al mercado | Plantilla (conglomerado) | Ciudades dentro de la ciudad | 6–8 s | Esfera de partículas sobre el mapa | Esfera se abre en pasillos por giro | Recorrido por pasillos; locales y giros |
| Baja la marea | Plantilla (territorio) | Islas de 15 minutos | 8–10 s | Territorio bajo el agua | Emergen primero las zonas completas | El agua se detiene en el umbral; cámara casi fija |
| El arco de las gemelas | Plantilla (par) | Colonias gemelas | 5–8 s | Colonia origen y su perfil | Arco de luz y la cámara lo sigue | Ambas colonias con perfiles superpuestos |
| El apagón | Plantilla (territorio) | Rarezas | 6–8 s | Territorio encendido | Se apagan primero las clases comunes | Órbita lenta sobre la constelación; aparecen los nombres |
| La hélice | Plantilla (alcaldía) | ADN de alcaldía | 6–10 s | Puntos se elevan del mapa | Se enrollan en hélice por sector | Órbita; transformación al comparar |
| Entre palabras | Plantilla (territorio) | Cómo se llaman las cosas | 8–12 s | Palabras flotan sobre sus zonas | Cámara avanza entre palabras | Palabras se agrupan por tipo |
| La ciudad se enciende en línea | Fijo | La ciudad que brilla en línea | 8–10 s | Ciudad en penumbra | Halos se encienden por alcaldía | Vista general de la brecha |

**Formato propio:** Theatre.js se usa solo como editor. Cada recorrido se exporta a un JSON propio (fotogramas clave relativos al territorio: cámara expresada en fracciones del encuadre, tiempos, curvas de aceleración) que GSAP reproduce en producción. El portal no carga Theatre.js.

**Diseño y prueba:** se diseñan sobre un territorio de referencia y se guardan como plantillas relativas. Cada plantilla se prueba con al menos tres territorios extremos (línea corta y larga, calle recta y curva, mercado pequeño y enorme). El Analista elige plantilla y territorio, nunca tiempos ni duraciones.

## Coreografía de transiciones

La transición estándar entre paneles dura entre 1.2 y 1.5 s, incluido el conteo de cifras, sigue tres tiempos solapados y nunca usa cortes bruscos. Las excepciones tienen tope declarado.

**Vocabulario de cámara:** órbita (contemplar), desplazamiento (recorrer), grúa (cambiar de escala), rasante (escala de calle) y arco de vuelo (subir, desplazarse y bajar para territorios lejanos). La única excepción al no-corte es la comparación lado a lado.

**Transición estándar**

| Fase | Empieza en | Duración |
| --- | --- | --- |
| Texto saliente | 0 s | 0.20 s |
| 1. Selección: atenuar y encender puntos | 0 s | 0.30 s |
| 2. Cámara: mover al nuevo encuadre | 0.20 s (al 67 % de la selección) | 0.50–0.75 s |
| 3. Forma: reorganizar los puntos | Al 70 % de la cámara | 0.50–0.70 s, escalonamiento incluido |
| Texto entrante y conteo de cifras | Al 50 % de la forma | 0.40 s |

Total: 1.2 s con los mínimos y 1.48 s con los máximos.

**Escalonamiento:** los puntos se mueven en oleada desde el centro del encuadre hacia afuera, con 0.2–0.4 s entre el primero y el último, dentro de la duración de la forma: el primer punto arranca al inicio de la fase, el último termina al final y cada punto anima durante la duración de la forma menos el escalonamiento.

**Matriz de transiciones**

| Cambio | Qué pasa | Duración total |
| --- | --- | --- |
| Solo la selección | Selección y conteo de cifras (este empieza a los 0.15 s) | 0.55 s |
| Territorio cercano, misma escena | Desplazamiento o grúa; transición estándar | 1.2–1.48 s |
| Territorio lejano | Arco de vuelo: cámara de 0.75 s + 0.05 s por cada km por encima de 3 km, máximo 1.6 s | Hasta 2.1 s |
| Entre escenas o modos geográficos | Forma directa; transición estándar | 1.2–1.48 s |
| Hacia, desde o entre modos abstractos | Los puntos regresan a su lugar en la ciudad y luego toman la nueva forma (secuencia abajo) | Hasta 1.7 s |
| Comparación lado a lado | División de pantalla con corte; la forma se anima en cada mitad | 0.7 s |
| Comparación por transformación | Transición estándar sin cámara | 1.0 s |

Un territorio es **cercano** si los centros de ambos encuadres están a 3 km o menos y la escala cambia 4 veces o menos; si no, es **lejano**.

**Secuencia con modos abstractos**

| Fase | Empieza en | Duración |
| --- | --- | --- |
| Selección | 0 s | 0.30 s |
| Regreso a la ciudad (cámara quieta) | 0.20 s | 0.50 s |
| Cámara | 0.55 s | 0.55 s |
| Forma abstracta | 0.95 s | 0.70 s |
| Texto entrante y cifras | 1.30 s | 0.40 s |

Así se respeta la regla de nunca tener dos movimientos fuertes al mismo tiempo: mientras los puntos regresan a la ciudad, la cámara no se mueve.

**Texto y cifras:** el texto anterior sale al iniciar; el nuevo entra a la mitad de la forma. Las cifras cuentan hasta su valor en 0.4 s y terminan exactamente en el valor real.

**Interrupciones**

- Avance a mitad de transición: se completa en 0.2 s y empieza la siguiente; nunca hay cola.
- Respuesta del Analista durante un recorrido: el recorrido se pausa y la respuesta entra como panel nuevo; se puede volver.
- Retroceso: transición inversa con la misma duración.

**Reposo:** brillo sutil u órbita imperceptible tras la transición; se detiene al interactuar.

**Movimiento reducido:** fundido de 0.3 s; recorridos como imágenes fijas por tiempo; misma información.

**Celular:** todas las duraciones se multiplican por 0.8 (estándar 0.96–1.18 s), escalonamiento de 0.1–0.2 s, agregados por AGEB o colonia y sin vuelos rasantes largos.

## Estado de avance

Corte: 8 nov 2026. Capa de datos avanzada; producto sin iniciar.

| Frente | Estado |
| --- | --- |
| Datos (`raw`, `staging`, `core`) | Cuatro ediciones cargadas; SCD tipo 2 y reconciliación; colonia, tramo y conglomerados (5 993, cinco fuentes); Censos Económicos 2024 y validación contra el DENUE |
| Capa `semantic` | 18 tablas: edicion, establecimiento, territorio, actividad, perfil_sector, conteo_clase, calle, conglomerado, dinamica, resumen_territorio, censo_sector, cobertura_censo, metro_estacion, metro_linea, metro_recorrido, colonia_gemela, palabra_nombre, lugar. Falta Islas de 15 minutos |
| Infraestructura | Clúster PostgreSQL 18 y tres roles operando |
| Prototipo 1 | Cerrado: compuerta de conglomerados en verde |
| Prototipo 2 | Cerrado: 60 FPS con todos los puntos en un S26 Ultra; faltan prueba con brillo y en gama media |
| Prototipo 3 | Cerrado: resuelve lugares con 87 % de acierto en casos nuevos; falta respaldo con modelo y probar con usuarios reales |
| Contrato de escena (H09) | Hecho: modelos, validación en tres niveles, herencia, forma canónica, migraciones, tipos TS y Ajv, CI sin base |
| Backend (API), frontend, Analista | Sin código |
| Diseño editorial | Sin guiones ni sistema visual |

**Desfases conocidos**

- Islas de 15 minutos no tiene red peatonal ni accesibilidad calculada (Pandana o r5py).
- `pgvector` está habilitado en la base, pero aún no hay embeddings para traducir giros ni perfiles de similitud vectoriales. El glosario de giros (lenguaje común → SCIAN) sigue pendiente.
- La edición DENUE 11/2026 se publica el 25 de noviembre: probar con ella la recarga y la reconciliación.

## Resultado del prototipo 1

Edición 2026-05 (462 729 establecimientos). Consulta reproducible: `dbt/analyses/prototipo1_compuerta_conglomerados.sql`.

| Métrica | Resultado |
| --- | --- |
| Establecimientos con tipo y nombre de conglomerado (campo DENUE) | 21.0 % (97 178) |
| Mercados del padrón (329) con un grupo MERCADO PUBLICO del DENUE que cruza su círculo y al menos 10 locales | 88.4 % (291) |
| Ídem, y además con nombre parecido (definición de la compuerta) | **82.1 %** (270) |

**Compuerta: verde** (umbral de 70 %). Ciudades dentro de la ciudad entra a la primera versión tal cual, sin sustituirla por Rarezas. Los conglomerados de `dim_conglomerado` ya incorporan además las otras fuentes (OSM, tianguis, mercados sobre ruedas), útiles para los casos fuera del campo.

**Otras coberturas (2026-05)**

| Campo | Cobertura |
| --- | --- |
| Nombre de vialidad | 100 % con valor; el tramo de calle se asigna 76.7 % por nombre, 6.8 % por nombre parecido, 15.1 % por cercanía y 1.4 % sin asignar |
| Sitio web | 10.6 % |
| Correo | 22.6 % |
| Sitio web o correo | 25.1 % |

**Notas y límites**

- La cobertura del campo es de 21.0 % en la tabla de pertenencia y 22.1 % en el campo crudo; la diferencia son registros cuyo punto no se pudo emparejar con su grupo. Conviene revisar esos casos.
- La coincidencia del padrón usa intersección espacial más similitud de nombre; no se revisó a mano una muestra. Un mercado grande vecino podría haberse contado por error: conviene validar unas 20 parejas antes de dar la cifra por definitiva.
- Redes sociales (Facebook, Twitter) no se midieron: el campo no está cargado en el modelo, así que "La ciudad que brilla en línea" solo cuenta web y correo por ahora.
- La presencia digital es baja (25 %): la escena mostrará una brecha real, pero el texto debe decir que mide presencia declarada.

## Resultado del prototipo 2

Implementado en `prototipos/02-renderizador/` (Vite + Three.js, WebGL2, un solo lienzo, fondo desde datos propios, 7 macrosectores con paleta provisional, encendido desde el Zócalo, selección que atenúa y telemetría). Paquete exportado de la base: 462 729 puntos en 3.2 MB (7 bytes por punto).

Costo de GPU por cuadro, medido con temporizador de GPU en una GTX 1660 SUPER (1080×873, recorrido de 12 s):

| Configuración | Mediana | p95 |
| --- | --- | --- |
| dpr 1, sin brillo | 3.55 ms | 4.75 ms |
| dpr 1, con brillo | 9.22 ms | 10.27 ms |
| dpr 2.5, sin brillo | 11.82 ms | 18.54 ms |

Lectura: dibujar todos los puntos es barato; el costo lo ponen el relleno de píxeles (resolución) y el brillo. En escritorio hay holgura para 60 FPS (16.7 ms).

**Prueba en celular real (9 nov 2026): superada.** Samsung S26 Ultra (Adreno 840), Chrome Android, ventana de 384×648 a dpr 1.5, sin brillo, con los 462 729 puntos y un recorrido de 12 s con zoom y órbita (720 cuadros):

| Métrica | Resultado |
| --- | --- |
| FPS promedio | 60 |
| FPS en el peor 5 % | 59.5 |
| Cuadro p95 | 16.8 ms |
| Cuadro máximo | 25 ms |

Cumple el criterio de 60 cuadros por segundo con todos los puntos. El temporizador de GPU no está disponible en este navegador móvil, así que no hay milisegundos de GPU; el techo de 60 FPS podría ocultar holgura o estar justo en el límite. Falta medir con brillo, en un teléfono de gama media (el presupuesto del diseño) y en iOS. Resultado crudo en `prototipos/02-renderizador/resultados/bench-movil-s26-ultra-2026-11-09.json`. El Artifact de prueba (sin brillo) es la versión del prototipo que se midió en el teléfono.

**Notas:** los FPS del navegador automatizado de desarrollo no son válidos (un lienzo vacío daba 5 FPS); por eso se mide GPU por cuadro.

## Resultado del prototipo 3

Implementado en `prototipos/03-resolver-lugar/`: la herramienta "Resolver lugar" del Analista (definición para la API de Claude en `herramienta.py`). Es determinista y sin modelo de lenguaje; lee solo la nueva vista `semantic.lugar`, un catálogo único de 14 mil lugares (ciudad, 16 alcaldías, 1 543 colonias, 163 estaciones, 2 885 conglomerados y 9 655 calles) con punto representativo, y un glosario CDMX de alias (`glosario.json`).

Entiende alcaldías y apodos ("GAM"), colonias y zonas que abarcan varias colonias ("la Roma" = Roma Norte y Roma Sur), estaciones y líneas del Metro, mercados, calles, errores de escritura ("Iztapalpa") y relaciones espaciales ("cerca del metro Balderas" = 500 m; "a 10 minutos del Zócalo" = 800 m). Responde con un estado (`resuelto`, `grupo`, `ambiguo`, `sin_resultado`, `fuera_de_cdmx`), confianza y una nota para el usuario; rechaza referencias personales ("mi casa") y municipios de fuera ("Toluca").

**Resultados** (128 formas de nombrar lugares, ejecutadas con el rol de solo lectura del Analista):

| Banco | Casos | Correctos | Nota |
| --- | --- | --- | --- |
| Ajuste | 66 | 66 | Se usó para desarrollar; no mide generalización |
| Ciego 1 | 38 | 33 antes de corregir (87 %); 38 después | Las 5 fallas fueron errores reales del resolutor y se corrigieron |
| Ciego 2 | 24 | 24 | Escrito y fijado antes de ejecutarlo; una sola corrida |

La cifra que mejor estima el desempeño con formas nuevas es la del banco ciego 1 antes de corregir: **87 %**. Los bancos ciegos los escribió el mismo equipo que el resolutor, así que probablemente sobrestiman el desempeño con usuarios reales. Una revisión a ojo del banco ciego 2 encontró un acierto falso ("Calzada de Tlalpan" devolvía otra vía) que las expectativas permisivas no detectaban; se corrigió y se endurecieron las expectativas. Tiempo por consulta: 110–250 ms por el túnel SSH (aún no medido desde el VPS).

**Hallazgos de datos:** el catálogo de calles guarda "Calzada de Tlalpan" como `DE TLALPAN` (sin el tipo de vía, con la preposición); "Eje Central" figura como Avenida Lázaro Cárdenas; existen polígonos de colonia duplicados con el mismo nombre ("Anzures"); y hay calles y estaciones llamadas como municipios de fuera ("Toluca", "Ecatepec").

**Pendiente:** respaldo con modelo ligero (Haiku) para formas que ningún método cubre; probar con preguntas reales de usuarios; alias de vías (ejes viales) y de más apodos; medir la latencia desde el VPS.

## Resultado del contrato de escena

Implementado en `backend/contracts/` (Python) y `backend/contracts-ts/` (navegador), el 14 nov 2026. El diseño y sus ajustes están en `docs/changes/2026-11-08-contrato-escena/spec.md`.

- **Fuente única:** modelos Pydantic v2 con tres escenas (Ciudad de luz, Corredores del Metro en línea y ranking, Ciudades dentro de la ciudad en exterior e interior). El esquema JSON, los tipos TypeScript y el validador Ajv se generan; `make contratos` falla si están desactualizados.
- **Lo que no cabe en el estado:** ninguna cifra, color, escala, coordenada ni duración. Los textos no admiten dígitos fuera de los huecos `{nombre}`; las cifras se nombran (`medida`, `fila`, `formato`) y deben existir en la vista exacta del estado.
- **Validación sin base:** estructura, referencias (archivo `referencias/2026-05.json`, 0.69 MB, exportado de `semantic` con el rol de solo lectura) y coherencia. Python y Ajv dan el mismo veredicto en los 49 casos del banco para los niveles 1 y 2.
- **Forma canónica:** Python y TypeScript producen los mismos bytes en 10 casos fijos y en 300 estados aleatorios con texto difícil (acentos en NFC y NFD, emoji, comillas, claves con `|`). Es la base del id por contenido de H14.
- **Verificación:** 148 pruebas de Python, 60 de Node, `make ci` en 4 s sin base y `make verify` en verde.
- **Pendiente:** crear el remoto público (con gitleaks sobre el historial) para que el workflow de GitHub Actions corra; hoy solo está escrito.

## Riesgos, primera versión y próximos pasos

Antes de construir, tres prototipos deciden la viabilidad: el renderizador sin mapa base, la cobertura de campos y la resolución de lugares.

**Riesgos**

| Riesgo | Mitigación |
| --- | --- |
| Rendimiento en celulares | Agregados por AGEB o colonia; prueba en gama media por escena |
| Espectáculo sin precisión | Regla de vista exacta, cifras vinculadas y prueba de paridad |
| Alucinación del Analista | Vistas semánticas, validación de SQL y de estado, banco de evaluación |
| Costo de la API | Modelo ligero para clasificar, caché de prompt y de intención, límites de uso y presupuesto con modo degradado |
| Campos incompletos | Medir cobertura antes de construir cada escena |
| Datos desactualizados | Fecha de corte visible en todas las vistas; paneles con edición y aviso de edición nueva |
| Cobertura insuficiente del campo conglomerado | Compuerta de decisión en el prototipo 1, enriquecimiento espacial y escena de reemplazo |
| Costo de la alternativa 2D por escena | Componentes 2D genéricos por tipo de resultado |
| Dependencia de Theatre.js | Formato propio de recorrido; Theatre.js solo como editor |

**Propuestas para los riesgos de la primera versión**

*Cobertura del campo conglomerado.* Ciudades dentro de la ciudad está en la primera versión y depende de un campo opcional.

1. **Medir dos coberturas en el prototipo 1:**
   - porcentaje de establecimientos con tipo y nombre de conglomerado;
   - porcentaje de mercados del padrón oficial de mercados públicos que aparecen en el DENUE con su nombre y al menos 10 locales.
2. **Compuerta de decisión:**
   - **Verde** (70 % o más de los mercados del padrón): se construye tal cual.
   - **Ámbar** (40 a 70 %): se construye con enriquecimiento espacial. Los establecimientos dentro del polígono o radio de un conglomerado conocido (padrón, OSM `amenity=marketplace` y `shop=mall`, Central de Abasto) se le asignan aunque el campo venga vacío. La vista exacta separa los locales que vienen del campo de los asignados por ubicación.
   - **Rojo** (menos de 40 %): en la primera versión se sustituye por Rarezas, que solo depende de SCIAN y ubicación; Ciudades dentro de la ciudad pasa a la segunda versión.
3. **Confirmar fuentes:** verificar que el padrón de mercados públicos tenga ubicación o polígono descargable; si solo hay puntos, usar un radio por mercado calibrado con su número de locales.

*Costo de la alternativa 2D.* Si cada escena necesita su propia versión 2D, el trabajo se duplica.

1. **La alternativa 2D es la vista exacta**, no una reinterpretación de la escena. Cada estado declara su tipo de resultado y un componente genérico lo dibuja:
   - Ranking: barras horizontales.
   - Territorial: coropleta 2D en SVG con las geometrías del paquete estático.
   - Comparación: barras pareadas o pequeños múltiplos.
   - Perfil (ADN, gemelas): barras de cociente o de perfil.
   - Serie (anillos): línea.
2. **Costo fijo:** son 5 componentes más la tabla, para todas las escenas presentes y futuras. Una escena nueva solo declara su tipo de resultado.
3. **Usos adicionales sin trabajo extra:** respaldo cuando no hay WebGL2, complemento del movimiento reducido, lectura con lector de pantalla (tabla con encabezados y resumen textual generado desde la narrativa) e imagen de vista previa de los enlaces compartidos, dibujada en el servidor desde el mismo SVG.
4. **Criterio de terminado:** una escena no está lista hasta que su vista exacta se lee completa con un lector de pantalla.

**Prototipos de validación**

1. **Cobertura de campos:** porcentaje de registros con conglomerado, presencia digital y nombre de vialidad utilizable, más la compuerta de conglomerados.
2. **Renderizador sin mapa base:** ciudad de luz con todos los puntos de CDMX y fondo propio, probada en celular, con una paleta provisional.
3. **Resolver lugar:** 50 formas reales de nombrar lugares de la ciudad.

**Primera versión (propuesta)**

- Escenas: ciudad de luz, corredores del Metro (modos línea y ranking) y ciudades dentro de la ciudad, o Rarezas si la compuerta sale en rojo.
- Una historia completa: Vida comercial del Metro.
- El Analista generando paneles, con 20 preguntas de evaluación verificadas a mano, límites de uso y caché de intención.
- Persistencia de paneles (`/p/{id}`, `/c/{id}`) y vista exacta con los componentes 2D genéricos.
- Página de metodología.

**Próximos pasos (en orden)**

- [x] Fijar la edición base del DENUE (05/2026) y actualizar las cifras de escala
- [x] Conseguir las ediciones anteriores del DENUE (05/2024, 11/2024, 05/2025; descargadas a mano)
- [x] Cargar las cuatro ediciones a `raw` y construir `staging` y `core` (dbt; ver `dbt/README.md`)
- [x] Prototipo 1: cobertura de campos y compuerta de conglomerados: **verde** (82.1 % del padrón; ver "Resultado del prototipo 1")
- [x] Prototipo 2: renderizador sin mapa base con paleta provisional (escritorio: GPU 3.55 ms por cuadro; S26 Ultra: 60 FPS, p5 59.5)
- [x] Prototipo 3: resolver lugar (87 % en casos nuevos; ver "Resultado del prototipo 3"); falta el glosario CDMX de giros (lenguaje común → SCIAN)
- [x] Contrato de escena en Pydantic v2 y exportación a JSON Schema (H09; ver "Resultado del contrato de escena")
- [x] Catálogo de vistas semánticas, primera versión: 18 tablas en `semantic` (ver `dbt/README.md`), con `lugar` para resolver lugares, incluidas Metro, Colonias gemelas y Cómo se llaman las cosas; falta la de Islas de 15 minutos
- [ ] Banco de preguntas de evaluación del Analista
- [ ] Guion panel por panel de "Vida comercial del Metro"
- [x] Macrosectores definidos (7 familias de sectores SCIAN; ver `docs/Core — Documentación del modelo de datos.md`, sección 4.11)
- [ ] Sistema visual: paleta por macrosector, tipografía, tratamiento de la luz
- [ ] Guion panel por panel de "Centro contra periferia"

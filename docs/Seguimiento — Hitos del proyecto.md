# Pulso DENUE CDMX — Seguimiento de hitos

Actualizado: 22 nov 2026 · Fuente de las decisiones: `docs/Pulso DENUE CDMX — Síntesis del proyecto.md` · Orden de trabajo: `docs/Plan de desarrollo — Primera versión.md`

Este documento lista los hitos para llegar a la primera versión pública y lo que queda para la segunda. Cada hito dice qué entrega, cuándo se da por terminado y de qué depende. Al cerrar un hito, se marca aquí y se registra el resultado en la síntesis.

**Estados:** ✅ hecho · 🟡 en curso · ⬜ pendiente

## Resumen

| ID | Hito | Fase | Estado | Depende de |
| --- | --- | --- | --- | --- |
| H01 | Base de datos en el VPS | Fundamentos | ✅ | — |
| H02 | Modelo de datos con cuatro ediciones | Fundamentos | ✅ | H01 |
| H03 | Capa `semantic`, primera versión | Fundamentos | ✅ | H02 |
| H04 | Prototipo 1: cobertura y compuerta de conglomerados | Validación | ✅ | H02 |
| H05 | Prototipo 2: renderizador sin mapa base | Validación | ✅ | H02 |
| H06 | Prototipo 3: resolver lugar | Validación | ✅ | H03 |
| H07 | Carga de la edición DENUE 11/2026 | Datos | ⬜ | H02 |
| H08 | Sistema visual | Definición | ✅ | H05 |
| H09 | Contrato de escena | Definición | ✅ | H03 |
| H10 | Traducir giro: glosario y embeddings | Definición | ✅ | H03 |
| H11 | Banco de evaluación del Analista | Definición | ⬜ | H06, H10 |
| H12 | Guion de "Vida comercial del Metro" | Definición | ✅ | H09 |
| H13 | Paquete estático y prueba de paridad | Construcción | ⬜ | H09 |
| H14 | Backend: validación y persistencia de paneles | Construcción | ⬜ | H09 |
| H15 | Motor de escenas y coreografía | Construcción | ⬜ | H05, H08, H09 |
| H16 | Escenas de la primera versión | Construcción | ⬜ | H13, H15 |
| H17 | Vista exacta y componentes 2D | Construcción | ⬜ | H09, H13 |
| H18 | Recorridos de autor | Construcción | ⬜ | H15, H16 |
| H19 | El Analista: orquestación y herramientas | Analista | ⬜ | H06, H09, H10, H11 (H19b: H14) |
| H20 | El Analista: caché, límites y observabilidad | Analista | ⬜ | H19 |
| H21 | Historia "Vida comercial del Metro" | Contenido | ⬜ | H12, H16, H18 |
| H22 | Página de metodología | Contenido | ⬜ | H03, H04 |
| H23 | Accesibilidad | Calidad | ⬜ | H17 |
| H24 | Rendimiento en dispositivos | Calidad | ⬜ fuera de la v1 | H16 |
| H25 | Despliegue y operación | Lanzamiento | ⬜ | H13, H14 |
| H26 | Lanzamiento de la primera versión | Lanzamiento | ⬜ | H07, H16 a H25 |
| H27 | Segunda versión | Después | ⬜ | H26 |

## Fase 1 · Fundamentos (hecha)

### H01 · Base de datos en el VPS ✅
Clúster PostgreSQL 18 con PostGIS y pgvector en `localhost:5433`, aislado del clúster 16, con los roles `pulso_owner`, `pulso_app` y `pulso_analista`.
- **Entregables:** `db/00_bootstrap.sql`, `db/INSTALAR_POSTGRES18.md`.
- **Resultado:** operando desde el 2 nov 2026.

### H02 · Modelo de datos con cuatro ediciones ✅
Capas `raw`, `staging` y `core` con dbt: hechos, dimensiones, SCD tipo 2, reconciliación entre ediciones, colonia, tramo de calle, conglomerados de cinco fuentes y Censos Económicos 2024.
- **Entregables:** `pipeline/`, `dbt/models/staging`, `dbt/models/core`, `docs/Core — Documentación del modelo de datos.md`.
- **Resultado:** ediciones 05/2024, 11/2024, 05/2025 y 05/2026 cargadas.

### H03 · Capa `semantic`, primera versión ✅
Dieciocho tablas documentadas, única superficie del Analista y fuente de las cifras de historias y fichas.
- **Entregables:** `dbt/models/semantic`, permisos de lectura para `pulso_app` y `pulso_analista`.
- **Pendiente heredado:** la tabla de Islas de 15 minutos (pasa a H27).

## Fase 2 · Validación (hecha)

### H04 · Prototipo 1: cobertura y compuerta de conglomerados ✅
Medir si los campos opcionales del DENUE sostienen sus escenas.
- **Resultado:** compuerta en verde (82.1 % de los mercados del padrón). Ciudades dentro de la ciudad entra a la primera versión. Presencia digital: 25.1 %.
- **Entregable:** `dbt/analyses/prototipo1_compuerta_conglomerados.sql`.

### H05 · Prototipo 2: renderizador sin mapa base ✅
Ciudad de luz con los 462 729 puntos en un solo lienzo WebGL2.
- **Resultado:** 3.55 ms de GPU por cuadro en escritorio; 60 FPS en un S26 Ultra (dpr 1.5, sin brillo).
- **Pendiente heredado:** probar con brillo, en gama media y en iOS (pasa a H24).

### H06 · Prototipo 3: resolver lugar ✅
Herramienta determinista sobre `semantic.lugar` y un glosario CDMX.
- **Resultado:** 87 % de acierto en casos nuevos (128 casos en total).
- **Pendiente heredado:** respaldo con modelo ligero y prueba con usuarios reales (pasa a H19 y H11).

## Fase 3 · Datos

### H07 · Carga de la edición DENUE 11/2026 ⬜
INEGI publica la edición el 25 nov 2026. Es la primera recarga real: prueba el pipeline de punta a punta.
- **Trabajo:** descargar, cargar a `raw`, reconstruir `staging`, `core` y `semantic`; revisar la reconciliación (métodos id, difuso, salto y reúso) y el cierre de bajas del SCD tipo 2.
- **Terminado cuando:** la nueva edición queda como vigente, la tasa de ids nuevos y las bajas son plausibles frente a las ediciones previas, y el resultado del prototipo 1 se vuelve a medir.
- **Decisión que habilita:** qué edición anterior se usa para comparar en el portal.

## Fase 4 · Definición

### H08 · Sistema visual ✅
Paleta definitiva por macrosector (7 colores), tipografía y tratamiento de la luz (brillo, halos, fondo).
- **Entregables:** tokens de color y tipografía; parámetros del shader de puntos y del posprocesado.
- **Terminado cuando:** los tokens salen de una sola fuente (`diseno/`), la paleta funciona con brillo aditivo sobre fondo oscuro sin que el Centro se queme a blanco, la variante clara cumple 3:1 de contraste sobre papel y el prototipo 2 los aplica. Intent en `docs/changes/2026-11-14-sistema-visual/`.
- **Decidido (14 nov 2026):** fuera de la primera versión, tanto el criterio de daltonismo como el de rendimiento (celular con brillo y gama media). Tema claro solo para la vista exacta 2D y la interfaz; la ciudad 3D solo en oscuro.
- **Resultado (15 nov 2026):** paleta vívida, brillo por posprocesado con mapeo `neutral` e Inter, elegidos en el laboratorio. `diseno/tokens.json` es la fuente única y el prototipo 2 la aplica. `make verify` en verde. Detalle en la síntesis.

### H09 · Contrato de escena ✅
El contrato central que escriben historias, explorador y Analista, y que interpreta un solo motor.
- **Entregables:** `backend/contracts/escena.py` (Pydantic v2) y `catalogo.py` con los valores por escena; `backend/contracts/escena.v1.json`; tipos TypeScript y validador Ajv generados; reglas de herencia; función de migración entre versiones.
- **Terminado cuando:** valida en tres niveles (estructura, referencias, coherencia), la integración continua rechaza una historia inválida y cubre las escenas de la primera versión.
- **Resultado (14 nov 2026):** `backend/contracts/` (modelos, validación en tres niveles, herencia, forma canónica y migraciones), `backend/contracts-ts/` (Ajv, tipos y forma canónica en TS), `contenido/historias/` y el workflow `.github/workflows/verificar.yml`. `make ci` (4 s, sin base) y `make verify` en verde. Pendiente: crear el remoto público para que el workflow corra en GitHub.

### H10 · Traducir giro: glosario y embeddings ✅
Segunda herramienta crítica del Analista: lenguaje común a clases SCIAN ("tiendita", "fonda", "estética").
- **Entregables:** glosario CDMX de giros; embeddings de clases SCIAN (Voyage AI o modelo multilingüe local); función `traducir_giro` con banco de pruebas.
- **Terminado cuando:** resuelve al menos 50 giros coloquiales con acierto medido en un banco ciego.
- **Resultado (15 nov 2026):** en `traducir-giro/`. Los embeddings solos no alcanzaron en el primer banco ciego (EmbeddingGemma, 79 % entre los primeros 5; el criterio era 85 %). La herramienta completa (glosario, lugar, 10 candidatos de EmbeddingGemma y `claude-haiku-5-5` que elige) **cumple en un segundo banco ciego: 91 % de acierto en 66 giros, 100 % de rechazo de lo que no es giro y 3 % de giros perdidos**. Detalle en `traducir-giro/README.md` y en la síntesis.
- **Cerrado (22 nov 2026), con dos decisiones de integración propuestas:**
  - **Dónde vive:** se queda en `traducir-giro/` como implementación de referencia hasta H19. En H19 entra al backend junto con resolver lugar, con el modelo y PyTorch en un grupo de dependencias aparte para que `make ci` siga ligero. No se mueve ahora a `prototipos/`: serían dos mudanzas en vez de una.
  - **Vectores (D3):** en archivo, no en pgvector. Son 948 vectores (2.9 MB) y la búsqueda en memoria tarda menos de 1 ms; lo caro es convertir la pregunta en vector, y eso exige cargar el modelo en el backend de todos modos. pgvector se reconsidera si una herramienta necesita buscar por significado entre los 460 mil establecimientos o en las notas de metodología.
- **Pasa a otros hitos:** banco ciego de la versión corregida (H11); cómo carga el modelo el backend en el VPS, catálogo de clases y vectores por edición y «cerca del metro» (H19); leer la licencia de Gemma antes de publicar (H25); regenerar catálogo y vectores con la edición 11/2026 (H07).

### H11 · Banco de evaluación del Analista ⬜
Preguntas sobre CDMX con respuestas verificadas a mano contra `semantic`.
- **Entregables:** al menos 20 preguntas para la primera versión (cuantitativas, metodológicas y mixtas), con cifra esperada, consulta de referencia y escena esperada; casos reales de usuarios para resolver lugar.
- **Terminado cuando:** corre en integración continua y reporta acierto por tipo de pregunta.
- **Plan (22 nov 2026):** se trabaja junto con H19a como un solo subproyecto, con línea base temprana y registro de experimentos. Plan en `docs/changes/2026-11-22-h11-banco-analista/plan.md`.

### H12 · Guion de "Vida comercial del Metro" ✅
Historia de 5 a 8 paneles sobre Corredores del Metro (modos línea y ranking).
- **Entregables:** guion panel por panel con pregunta, estado de escena, cifra vinculada, nota de cautela y recorrido.
- **Terminado cuando:** cada panel valida contra el contrato (H09) y sus cifras salen de `semantic`.
- **Decidido (14 nov 2026):** el guion no lleva un panel con cifras por giro ("dónde se come junto al Metro"). En Corredores del Metro la selección por giro solo atenúa puntos; las cifras no cambian, porque `semantic.metro_estacion` no tiene conteos por giro. Pasa a H27.
- **Resultado (14 nov 2026):** `contenido/historias/vida-comercial-metro.yml`, 6 paneles con pregunta, estado, cifras vinculadas, nota de cautela y recorrido; valida contra el contrato y sus cifras se comprobaron en `semantic`. Pidió siete ajustes al contrato (spec de H09) y dos en `semantic`: estaciones del Estado de México fuera del ranking (`en_cdmx`) y nombres cortos de giro (`ref_subsector_corto`). De paso se reescribió `colonia_gemela` (de 4.5–55 min a 2.5 min, mismo resultado). `make verify` en verde.

## Fase 5 · Construcción

### H13 · Paquete estático y prueba de paridad ⬜
Lo que el navegador descarga por edición, servido desde CDN.
- **Entregables:** puntos en binario (base: `prototipos/02-renderizador/exportar_paquete.py`, ampliado con clase SCIAN, colonia y AGEB), agregados por unidad oficial, geometrías simplificadas, resultados precalculados de historias y catálogo de referencias.
- **Terminado cuando:** la prueba de paridad compara cifras del paquete y del conteo en navegador contra `semantic` y detiene la publicación ante cualquier diferencia.

### H14 · Backend: validación y persistencia de paneles ⬜
FastAPI como fuente del contrato y del estado compartible.
- **Entregables:** validación de estados; tablas `app.panel` y `app.conversacion`; identificador por contenido (SHA-256 en base62); rutas `/p/{id}` y `/c/{id}`; resultados congelados; aviso de edición nueva.
- **Terminado cuando:** guardar es idempotente y un panel de una edición anterior abre con sus cifras originales.

### H15 · Motor de escenas y coreografía ⬜
Vue 3 + Three.js con lienzo persistente: los paneles cambian estado, el canvas no se destruye.
- **Entregables:** motor que interpreta el contrato; transiciones con GSAP según la matriz de coreografía (estándar de 1.2–1.5 s, arco de vuelo, modos abstractos); interrupciones; reposo; versión celular con agregados.
- **Terminado cuando:** las transiciones cumplen los tiempos de la síntesis y la continuidad visual se mantiene (el mismo punto viaja entre vistas).

### H16 · Escenas de la primera versión ⬜
- **Ciudad de luz:** escena neutra de inicio y de paso.
- **Corredores del Metro:** modos línea y ranking; radio de 300, 500 u 800 m.
- **Ciudades dentro de la ciudad:** modos exterior e interior.
- **Terminado cuando:** cada escena responde su pregunta, tiene vista exacta (H17) y se lee completa con lector de pantalla.

### H17 · Vista exacta y componentes 2D ⬜
La alternativa 2D es la vista exacta, no una reinterpretación de la escena.
- **Entregables:** cinco componentes genéricos (ranking, territorial, comparación, perfil, serie) más la tabla, con cifra, fecha de corte y descarga.
- **Terminado cuando:** sirven de respaldo sin WebGL2, de lectura con lector de pantalla y de imagen de vista previa de los enlaces compartidos.

### H18 · Recorridos de autor ⬜
Movimientos de cámara diseñados en Theatre.js y reproducidos con GSAP desde un formato propio.
- **Entregables:** formato JSON relativo al territorio; El despertar, Tren de luz, Constelación de estaciones y Entrar al mercado.
- **Terminado cuando:** cada plantilla se prueba con tres territorios extremos y el portal no carga Theatre.js.

## Fase 6 · El Analista

### H19 · Orquestación y herramientas ⬜
Ciclo de uso de herramientas de la API de Claude: Haiku clasifica, resuelve lugares y traduce giros; Sonnet escribe SQL, interpreta y redacta.
- **Entregables:** las cinco herramientas (resolver lugar, traducir giro, consultar datos, buscar metodología, construir escena); text-to-SQL con validación sqlglot sobre vistas autorizadas; RAG metodológico; respuesta con cifra, fecha de corte, consulta usada y panel.
- **Terminado cuando:** supera el banco de evaluación (H11) y nunca escribe cifras que no vengan de una consulta.
- **Decidido (22 nov 2026): se parte en dos.**
  - **H19a · El Analista como librería** (`backend/analista/`): ciclo de herramientas, las cinco herramientas y el prompt, medido contra el banco de H11. *Construir escena* valida con `contracts.validar` (H09), así que no espera a H14. Se trabaja junto con H11.
  - **H19b · Integración con la API:** guarda cada respuesta como panel (`app.panel`, `/p/{id}`) con resultados congelados. Espera a H14.
  - La respuesta del Analista se define desde H19a como modelo Pydantic, para que H19b la guarde tal cual.

### H20 · Caché, límites y observabilidad ⬜
- **Entregables:** caché de intención; límites por IP, conversación y pregunta; Cloudflare Turnstile; presupuesto con modo degradado; Langfuse autoalojado.
- **Terminado cuando:** dos preguntas con la misma intención comparten panel y al llegar al tope de presupuesto el portal pasa a modo degradado con aviso.

## Fase 7 · Contenido

### H21 · Historia "Vida comercial del Metro" ⬜
- **Entregable:** la historia del guion (H12) navegable, con indicador de posición y salida a "explorar desde aquí".
- **Terminado cuando:** cada panel tiene dirección propia (`/historias/{slug}/{n}`) y sus cifras pasan la prueba de paridad.

### H22 · Página de metodología ⬜
- **Entregable:** cobertura de campos (resultados de H04), versiones SCIAN, fechas de corte, reconciliación entre ediciones, límites del DENUE y descargas.
- **Terminado cuando:** cada cifra del portal puede rastrearse hasta su fuente desde esta página.

## Fase 8 · Calidad y lanzamiento

### H23 · Accesibilidad ⬜
- **Trabajo:** movimiento reducido (fundido de 0.3 s, recorridos como imágenes fijas), lectura con lector de pantalla, navegación por teclado y contraste.
- **Terminado cuando:** cada escena de la primera versión cumple el criterio de terminado de la síntesis.

### H24 · Rendimiento en dispositivos ⬜
- **Trabajo:** medir cada escena en un celular de gama media Android, en iOS y con brillo; definir el umbral para cambiar a agregados por AGEB o colonia.
- **Terminado cuando:** 60 FPS en escritorio y al menos 30 FPS estables en gama media, con resultados guardados en el repositorio.
- **Decidido (14 nov 2026):** fuera de la primera versión. No se mide rendimiento en dispositivos ni se define el umbral para cambiar a agregados; el criterio de 60 FPS queda sin comprobar. Se retoma después del lanzamiento. Los agregados por AGEB o colonia siguen en el diseño del paquete (H13).

### H25 · Despliegue y operación ⬜
- **Entregables:** contenedores Docker detrás de Traefik, estáticos en CDN, respaldo diario de la base con retención de 7 días, publicación de una edición nueva como procedimiento documentado.
- **Terminado cuando:** una edición nueva se publica sin pasos manuales fuera del procedimiento.

### H26 · Lanzamiento de la primera versión ⬜
- **Alcance:** las tres escenas (H16), una historia (H21), el Analista con límites (H19, H20), paneles compartibles (H14), vista exacta (H17) y metodología (H22).
- **Terminado cuando:** todos los hitos previos están cerrados con la edición vigente más reciente, salvo H24 (rendimiento en dispositivos), que queda fuera de la primera versión por decisión del 14 nov 2026.

## Fase 9 · Segunda versión

### H27 · Segunda versión ⬜
- **Escenas:** La ciudad que brilla en línea, Las calles hablan, Islas de 15 minutos (red peatonal y su tabla en `semantic`), El ADN de cada alcaldía, Colonias gemelas, Rarezas, Cómo se llaman las cosas y Anillos de densidad.
- **Historias y fichas:** Centro contra periferia; fichas por alcaldía y por sector.
- **Extensiones:** Metrobús y Tren Ligero, zona caminable por red peatonal, WebGPU.
- **Cifras por giro en Corredores del Metro** (viene de H12): conteos por estación y giro SCIAN en `semantic`, para que elegir un giro cambie también las cifras y no solo atenúe puntos. Responde preguntas como "¿qué estación tiene más farmacias?" en el explorador y el Analista. Pide cambio en dbt y `make build`, y una medida nueva en el contrato.

## Decisiones pendientes

| Decisión | Cuándo se toma | Hito que la necesita |
| --- | --- | --- |
| Edición anterior para comparar en el portal | Tras H07 | H13, H22 |
| Paleta, tipografía y tratamiento de luz | H08 | H15 |
| Guion completo de las dos historias | H12 y H27 | H21 |
| Proveedor de embeddings (Voyage AI o modelo local) | H10 | H19 |
| Umbral de rendimiento para cambiar a agregados | Fuera de la v1 (decisión del 14 nov 2026) | — |

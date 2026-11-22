# Plan: ruta del Analista

Estado: propuesto (22 nov 2026), sin ejecutar · Cadena: `H10 ✅ → H11 + H19a → H19b → H20` · Rutas: `docs/Plan de desarrollo — Primera versión.md`, sección "Rutas" · Detalle de la primera etapa: `docs/changes/2026-11-22-h11-banco-analista/plan.md`

Este documento ordena la ruta completa del Analista, desde el banco de evaluación hasta el Analista público con límites. La primera etapa tiene su propio plan detallado. Las otras dos se dejan a nivel de plan, porque H19b y H20 son hitos grandes y llevan intent, spec y plan propios cuando les toque.

## La ruta en una tabla

| Etapa | Hitos | Qué entrega | Necesita de otras rutas | Permisos |
|---|---|---|---|---|
| **A · Medir y afinar** | H11 + H19a | Banco de 50 casos, calificador y un Analista como librería que lo supera en el ciego | Nada | Solo lectura en la base; gasto de API con tope (D5) |
| **B · Conectar** | H19b | El Analista detrás de la API, con cada respuesta guardada como panel con dirección estable | H14 (ruta Backend) | Las tablas de H14 las crea H14 |
| **C · Abrir al público** | H20 | Caché de intención, límites, Turnstile, presupuesto con modo degradado y observabilidad | H25 para operar en el VPS | Servicios externos (Turnstile) y Langfuse en el VPS |

La etapa A es la única que no espera a nadie, y es donde está el aprendizaje de afinar un modelo contra un conjunto de datos. Las etapas B y C son integración y operación.

## Etapa A · Medir y afinar (H11 + H19a)

Todo el detalle está en `docs/changes/2026-11-22-h11-banco-analista/plan.md`. Resumen de sus pasos:

| Paso | Qué | Necesita | Cierra |
|---|---|---|---|
| 1 | Formato del caso (Pydantic) y `validar_banco.py` en `make ci` | nada | |
| 2 | Banco de ajuste: 30 casos, cada cifra verificada por dos caminos; `esperado/2026-05.json` | túnel | |
| 3 | Banco ciego: 20 casos escritos por un agente aislado, antes de construir el Analista | nada | |
| 4 | Modelo `Respuesta` (se acuerda con Ricardo), calificador e informe por tipo | nada | **H11** |
| 5 | Línea base: Sonnet + consultar datos; 3 corridas para medir el ruido | túnel y llave | |
| 6 | Experimentos: resolver lugar, traducir giro, construir escena, buscar metodología y ajustes de prompt, uno por uno, con registro | túnel y llave | |
| 7 | Corrida ciega única contra D2 | túnel y llave | **H19a** |
| 8 | Repaso en `laboratorio/analista.html` y cierre | nada | |

Las decisiones D1 a D5 de ese plan (tamaño del banco, umbral, juez con modelo, casos reales y tope de gasto) se toman antes del paso 1. D5 es necesaria antes del paso 5.

Modelos de partida: `claude-sonnet-5-5` para el ciclo y `claude-haiku-5-5` para las herramientas ligeras, los mismos que traducir giro. Cambiar de modelo es un experimento más y se anota en el registro.

## Etapa B · Conectar (H19b)

Empieza cuando H14 esté terminado. Antes de escribir código se hacen intent, spec y plan propios.

**Qué entra:**

- Una ruta de la API que recibe la pregunta y devuelve la `Respuesta` de H19a, sin cambiar su forma.
- Guardar cada respuesta como panel en `app.panel`, con id por contenido, consulta usada y resultados congelados, y la conversación en `app.conversacion`.
- Preguntas de seguimiento dentro de una conversación: el Analista recibe los paneles anteriores. Es lo único nuevo para el Analista mismo, así que se agregan al banco casos de seguimiento y se mide con el mismo calificador antes de cerrar.
- Cómo carga el backend el modelo de traducir giro en el VPS (1.2 GB por proceso). Propuesta: un solo proceso lo tiene y lo carga la primera vez que el glosario no resuelve (decisión de H10).
- Resolver lugar desde el VPS: hoy tarda de 110 a 250 ms por el túnel. Se mide en el servidor.
- La llave de la API en producción, en el `.env` del servidor y nunca en el repo.

**Terminado cuando:**
- La misma pregunta, hecha por la API, da la misma `Respuesta` que la librería.
- El panel abre en `/p/{id}` con sus cifras congeladas.
- El banco sigue en el nivel de H19a, ahora con los casos de seguimiento.

## Etapa C · Abrir al público (H20)

Está descrita en la síntesis ("Límites de uso del Analista público" y "Caché de intención"). Lleva intent, spec y plan propios.

| Pieza | Qué hace | Se puede adelantar en la etapa A |
|---|---|---|
| Límites por pregunta | 6 herramientas, 2 reintentos de SQL, tope de tokens | **Sí, ya están en H19a** para medir con las reglas de producción |
| Caché de intención | Dos preguntas con la misma intención comparten panel; se invalida al cambiar de edición | Parcial: la intención (lugar, clases, métrica, escena) ya sale de las herramientas y se puede registrar en cada respuesta |
| Presupuesto y modo degradado | Tope diario y mensual en dólares; al llegar, solo caché y explorador | El costo por pregunta ya se mide en los experimentos; sirve para fijar el tope |
| Límites por IP y conversación | 10 preguntas cada 10 min y 60 al día; 40 turnos | No: necesita la API |
| Turnstile | Verificación anti-bots en la primera pregunta | No |
| Langfuse autoalojado | Preguntas, herramientas, SQL y costo en producción | No hace falta: en la etapa A basta con las respuestas grabadas en JSON |

**Terminado cuando:**
- Dos preguntas con la misma intención comparten panel.
- Al llegar al tope de presupuesto, el portal pasa a modo degradado con aviso.

## Cruces con otras rutas

| Con | Qué pasa | Qué hacer |
|---|---|---|
| **Datos (H07, 25 nov)** | La edición vigente cambia y las cifras esperadas también | Regenerar `esperado/2026-11.json` y revisar la diferencia a mano; correr otra vez la línea base si ya existía. Conviene terminar el paso 2 antes del 25 |
| **Datos (H07)** | Cambia el catálogo de clases de traducir giro | Regenerar `clases.json` y los vectores antes de usar traducir giro en los experimentos |
| **Contenido (H22)** | Las notas de metodología definitivas | Hasta entonces, buscar metodología usa la sección "Conocimiento base del DENUE" y `_semantic.yml`; al llegar H22 se cambia la fuente y se mide como experimento |
| **Backend (H14)** | Persistencia de paneles | Bloquea la etapa B, no la A. La forma de `Respuesta` se acuerda en el paso 4 para que H14 la guarde tal cual |
| **Salida (H25)** | Despliegue en el VPS | La etapa C opera allí; la memoria del modelo de traducir giro entra al dimensionamiento |

## Lo que Ricardo decide o hace

| Cuándo | Qué |
|---|---|
| Antes del paso 1 | D1 a D4 del plan de H11 |
| Antes del paso 5 | **D5: tope de gasto en dólares** para los experimentos |
| Paso 3 | Revisar que las preguntas del ciego suenen a CDMX |
| Paso 4 | Aceptar la forma de `Respuesta` |
| Pasos 2 a 6 | Conseguir de 5 a 10 personas que escriban preguntas reales (D4) |
| Paso 7 | Dar por cerrada la etapa de afinado y autorizar la corrida ciega |
| Etapa B | Aceptar intent, spec y plan de H19b; el DDL de H14 ya habrá sido autorizado |
| Etapa C | Presupuesto de producción; alta en Turnstile; Langfuse en el VPS |

## Arranque de la siguiente sesión

1. Leer este plan y `docs/changes/2026-11-22-h11-banco-analista/plan.md`.
2. Rama `ruta-analista` (desde `main` con el PR #5 de H10 fusionado). Ya contiene los planes de H07, H11 y esta ruta, la sección "Rutas" del plan de desarrollo y el ajuste de dependencias de H19.
3. Pedir a Ricardo D1 a D5 si no están en el plan. Sin D5 se puede avanzar hasta el paso 4.
4. Empezar el paso 1 del plan de H11: modelo Pydantic del caso y `validar_banco.py`, en `backend/evaluacion/`, con su entrada en `make ci`.
5. Si ya pasó el 25 nov, revisar primero la ruta Datos: H07 tiene prioridad porque cambia las cifras del banco.
6. Antes de dar algo por terminado: `make verify` con la salida a la vista.

# Plan: traducir giro (H10)
Estado: propuesto (2026-11-15), sin ejecutar · Ref: H10 en `docs/Seguimiento — Hitos del proyecto.md` · Antecedentes: `docs/Herramientas del Analista.md` y el prototipo 3 (`prototipos/03-resolver-lugar/`)

**Actualización (15 nov 2026):** la capa de embeddings (pasos 1, 2 y 4) se trabaja primero como subproyecto independiente en `traducir-giro/`, todo en local, comparando Qwen3-Embedding-0.6B, EmbeddingGemma y multilingual-e5-small (BGE-M3 salió por peso). Su planteamiento y criterios de logro están en `traducir-giro/README.md` y mandan sobre este plan donde difieran. El glosario y el paso de Haiku se retoman con el modelo ya elegido. **Resultado (15 nov 2026):** los embeddings solos no cumplieron en el banco ciego; se eligió EmbeddingGemma como generador de candidatos y los pasos 3, 5, 6 y 7 se construyeron en `traducir-giro/` (no en `prototipos/04-traducir-giro/`). Falta correr el segundo banco ciego y el paso 8.

Quien no vio la conversación debería poder implementar H10 con este plan. No hay intent ni spec separados: el diseño se acordó en conversación el 15 nov 2026 y queda escrito aquí.

## Qué se construye

Una herramienta del Analista, `traducir_giro`, que convierte la forma común de nombrar un giro ("tiendita", "fonda", "donde arreglan celulares") en clases SCIAN. Trabaja en tres capas, de la más confiable a la más flexible:

1. **Glosario.** Lista escrita a mano de giros de CDMX y sus clases. Si el término está, se responde sin modelo.
2. **Embeddings.** Si el glosario no lo tiene, se buscan por significado las clases más parecidas. Esta capa no decide: solo entrega candidatos.
3. **Haiku elige.** Un modelo ligero recibe el término y los candidatos, y elige cuáles corresponden, o dice que ninguno.

Cuando ninguna capa alcanza confianza, la herramienta lo dice. Nunca inventa una clase.

## Decisiones ya tomadas

- **Orden de capas:** glosario, luego embeddings, luego Haiku (15 nov 2026).
- **Jev (modelo "Sistema Uno") queda fuera.** Elige entre 255 opciones como máximo y hay 948 clases; su precisión no está probada en español ni en SCIAN, y es una dependencia con lista de espera. Se reconsidera solo si el paso de Haiku resulta caro o lento.
- **Molde:** el del prototipo 3: glosario en JSON, función determinista, definición de herramienta, bancos de ajuste y ciegos, y un evaluador que escribe resultados.
- **La base real no se toca hasta el final**, y solo con permiso explícito.

## Decisiones abiertas (las resuelve Ricardo)

| # | Decisión | Propuesta | Cuándo |
|---|---|---|---|
| D1 | Modelo de embeddings | Local y multilingüe. Se elige midiendo dos o tres candidatos en el banco, no por reseñas | Paso 4 |
| D2 | Umbral de acierto para cerrar | 85 % en el banco ciego (el prototipo 3 cerró con 87 %) | Antes del paso 6 |
| D3 | Dónde viven los vectores en producción | Tabla con pgvector, expuesta en `semantic` | Paso 8 |
| D4 | Llave de la API de Claude para Haiku | En `.env`, como `ANTHROPIC_API_KEY`; la crea Ricardo | Antes del paso 5 |

Una consecuencia de D1 que conviene saber desde ahora: con un modelo local, el backend tendrá que cargarlo en el VPS para convertir en vector cada pregunta. Un modelo chico ocupa del orden de cientos de MB de memoria; uno grande, más de 2 GB. El tamaño del modelo entra en la elección.

## Datos de partida

Ya conocidos (no hace falta consultar):

- `semantic.actividad`: catálogo de clases SCIAN presentes en el DENUE, con jerarquía (subrama, rama, subsector, sector, macrosector), nombre normalizado y `establecimientos_vigente`. Su descripción ya dice "para traducir giros a clases".
- 948 clases en SCIAN 2023 (dato del plan de H09). La edición 05/2024 usa SCIAN 2018; `clase_scian_2023` da la equivalencia.
- `backend/contracts/referencias/2026-05.json` trae los códigos SCIAN válidos, de sector a clase. Sirve para validar el glosario sin base.
- `pgvector` está habilitado y vacío.

Por consultar en el paso 1 (solo lectura, rol `pulso_analista`, con túnel):

- Cuántas clases tienen al menos un establecimiento vigente, y cuántas concentran el 95 % de los establecimientos.
- Las palabras más frecuentes de los nombres comerciales por clase, desde `semantic.establecimiento`. Sirven para enriquecer el texto de cada clase ("ESTETICA", "TAQUERIA") y para sembrar el glosario.

## Forma de la respuesta

Igual en espíritu que resolver lugar:

| Estado | Significado |
|---|---|
| `resuelto` | Una clase |
| `grupo` | Varias clases que juntas forman el giro ("restaurante" abarca varias) |
| `ambiguo` | Hay lecturas distintas; el Analista debe preguntar ("papelería": ¿venta o fabricación?) |
| `sin_resultado` | No hay clase con confianza suficiente |
| `no_es_giro` | El texto no nombra una actividad económica |

Cada respuesta lleva además: las clases (código, nombre y establecimientos vigentes), la `capa` que resolvió (glosario, embeddings o modelo), `confianza` (alta, media, baja) y una `nota` para el usuario.

Una entrada del glosario puede apuntar a una clase o a un nivel superior (subrama o rama) cuando el giro común es más amplio que cualquier clase.

## Orden de trabajo

Cada paso termina con sus pruebas en verde antes de pasar al siguiente. Rama: `h10-traducir-giro`, desde `main`.

### Paso 1 · Reconocimiento de los datos (solo lectura)
- Consultar lo listado en "Por consultar" y anotar las cifras en este plan, en "Datos de partida".
- Exportar a `data/` (no versionado) el catálogo de clases con su jerarquía, conteo y palabras frecuentes. Es el insumo de los pasos 3 y 4, para no depender del túnel.
- Sin escritura en la base.

### Paso 2 · Bancos de prueba, antes que el código
- `prototipos/04-traducir-giro/casos_ajuste.json`: unos 60 giros para escribir y afinar el glosario.
- `casos_ciegos.json`: al menos 50 giros que **no** se miran al escribir el glosario ni al afinar umbrales. Se redactan en una sesión aparte, sin el glosario a la vista.
- Cada caso: término, estado esperado y conjunto de clases aceptables. Mezcla obligada: giros de glosario ("tiendita"), descripciones libres ("donde arreglan celulares"), ambiguos, textos que no son giro ("la Roma", "barato") y errores de dedo.
- Las clases esperadas se verifican a mano contra `semantic.actividad`. Los bancos se revisan a mano; no se regeneran para que una prueba pase.

### Paso 3 · Capa 1: glosario
- `glosario.json`: término normalizado, variantes, clases o nivel superior, y nota opcional. Sembrado con los giros de CDMX (tiendita, fonda, estética, tianguis, papelería, tlapalería, cocina económica…) y con las palabras frecuentes del paso 1.
- `traducir_giro.py`: normaliza (mayúsculas, sin acentos, plurales y diminutivos simples), busca exacto, luego por variantes, luego por parecido de trigramas contra el glosario y contra `nombre_clase_norm`.
- Prueba sin base: todos los códigos del glosario existen en `referencias/2026-05.json`. Entra a `make ci`.
- Medición: acierto de la capa 1 sola en el banco de ajuste.

### Paso 4 · Capa 2: embeddings (decide D1)
- Texto por clase: nombre de la clase, su jerarquía, el nombre corto del subsector y las palabras frecuentes de sus establecimientos.
- `embeddings.py`: genera los vectores de las clases y los guarda en `data/` como archivo. Con menos de mil vectores, la búsqueda por coseno en memoria es instantánea; pgvector no hace falta para medir.
- Comparar dos o tres modelos locales multilingües (candidatos: multilingual-e5-small, bge-m3 y uno compacto reciente). Métrica: en cuántos casos la clase correcta aparece entre los 5 y entre los 10 primeros candidatos. También tamaño en disco, memoria y tiempo por consulta.
- Solo se miden sobre el banco de ajuste. El ciego no se toca.
- Salida: tabla comparativa en `resultados_embeddings.md` y la elección de Ricardo (D1).

### Paso 5 · Capa 3: Haiku elige (necesita D4)
- Entrada: el término del usuario y los candidatos de la capa 2 (código, nombre, jerarquía y conteo).
- Salida estructurada: las clases elegidas dentro de los candidatos, o "ninguna", más el estado (`resuelto`, `grupo`, `ambiguo`, `no_es_giro`). El modelo no puede devolver un código que no esté entre los candidatos; si lo hace, se descarta.
- Modelo: Haiku vigente (`claude-haiku-5-5`), con el catálogo de instrucciones en caché de prompt.
- Las respuestas del modelo sobre los bancos se guardan en un archivo, para que la evaluación sea repetible y no gaste en cada corrida.
- Esta capa no corre en `make ci`: necesita llave y no es determinista.

### Paso 6 · Evaluación y cierre de la medición (necesita D2)
- `evaluar.py`: corre los bancos y escribe `resultados.md` y `resultados_ciegos.md`, con el acierto total y el que aporta cada capa (solo glosario; glosario más embeddings; las tres).
- `evaluar.py` sale con error si hay casos fallidos por debajo del umbral, a diferencia del evaluador del prototipo 3, que termina en 0 siempre.
- `make eval-giro` (necesita túnel y, para la capa 3, llave).
- El banco ciego se corre **una vez**, al final. Si el resultado no alcanza D2, los casos fallidos pasan al banco de ajuste y se escribe un segundo banco ciego, como se hizo en el prototipo 3.

### Paso 7 · Definición de la herramienta y repaso en el laboratorio
- `herramienta.py`: definición para el ciclo de herramientas de la API de Claude y su ejecución, igual que la de resolver lugar. La descripción le dice al modelo que la use siempre antes de consultar por giro y que nunca adivine códigos.
- `laboratorio/giros.html`: muestra, para cada caso de los bancos, qué devolvió cada capa (glosario, candidatos de embeddings con su parecido, elección de Haiku) y si acertó. Lee un JSON que exporta `evaluar.py`; no necesita base ni llave.
- Límite conocido del repaso: encender en la ciudad los puntos de una clase necesita la clase SCIAN en el paquete de puntos, que llega con H13. Hasta entonces el laboratorio muestra clases y conteos, no puntos.

### Paso 8 · Carga a la base real (solo con permiso; decide D3)
- Este paso escribe en la única base, que es la real. No se ejecuta sin que Ricardo lo pida en ese momento.
- Propuesta: el pipeline carga los vectores a una tabla en `raw`, y dbt los expone en `semantic` como tabla documentada en `_semantic.yml`, con pruebas de grano (una fila por versión SCIAN y clase) y de paridad contra `semantic.actividad`.
- Requiere `make build`, que también se pide, no se corre por cuenta propia.
- Alternativa si se prefiere no tocar la base todavía: el backend carga los vectores desde archivo y este paso se pospone a H19.

### Paso 9 · Cierre del hito
- `make verify` en verde y su salida a la vista.
- README del prototipo 4, con piezas, cómo correrlo, resultados y límites.
- Marcar H10 en el seguimiento, registrar "Resultado de traducir giro" en la síntesis y actualizar `docs/Herramientas del Analista.md`.
- Pull request hacia `main`.

## Qué queda fuera

- **El ciclo completo del Analista** (H19): aquí se entrega la herramienta y su definición, no la orquestación.
- **Preguntas reales de usuarios:** llegan con H11.
- **Buscar metodología:** usa embeddings de textos largos y es otra herramienta.
- **Ediciones en SCIAN 2018:** la herramienta responde en SCIAN 2023; la equivalencia hacia 2018 ya está en `semantic.actividad`.

## Riesgos

- **Un giro común rara vez es una sola clase.** "Restaurante" o "taller" abarcan varias. Por eso existe el estado `grupo` y los bancos aceptan conjuntos de clases.
- **Los nombres oficiales de las clases son largos y parecidos entre sí** ("Comercio al por menor de…"). Los embeddings pueden confundirlos; enriquecer el texto con palabras de los nombres comerciales es la apuesta para separarlos. Si no alcanza, se agregan las descripciones oficiales del SCIAN ("incluye" y "excluye"), que hoy no están en la base.
- **El banco ciego deja de ser ciego si se mira.** Se corre una vez y los fallos pasan al banco de ajuste.
- **Memoria en el VPS** para el modelo local (ver D1).

## Criterio de terminado

Resuelve al menos 50 giros coloquiales del banco ciego con el acierto acordado en D2, el resultado reporta cuánto aporta cada capa, y `make verify` está en verde.

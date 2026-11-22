# Pulso DENUE CDMX — Herramientas del Analista

Borrador del 15 nov 2026 · Fuentes: `docs/Pulso DENUE CDMX — Síntesis del proyecto.md` (sección "El Analista") y `docs/Seguimiento — Hitos del proyecto.md` (H10, H11, H19, H20)

El Analista es un analista senior experto en el DENUE que nunca inventa cifras. Para lograrlo no responde de memoria: llama a herramientas, y cada cifra que escribe viene de una consulta a la capa `semantic`. Este documento lista esas herramientas, qué hace cada una, de qué depende y en qué estado está.

## Cómo se reparte el trabajo

Hay dos modelos, cada uno con su papel:

- **Modelo ligero (Haiku):** clasifica la pregunta, resuelve lugares y traduce giros. Son tareas cortas y baratas.
- **Modelo capaz (Sonnet):** escribe el SQL, interpreta el resultado y redacta la respuesta.

El ciclo es siempre el mismo: clasifica la pregunta, resuelve el lugar y traduce el giro, consulta, valida y responde con cifra, contexto, fecha de corte, consulta usada y estado de escena.

## Las cinco herramientas

| # | Herramienta | Qué hace | Modelo | Hito | Estado |
|---|---|---|---|---|---|
| 1 | Resolver lugar | Convierte "la Roma" o "cerca del metro Balderas" en identificadores territoriales | Haiku | H06 (prototipo), H19 | Prototipo hecho: 87 % de acierto en casos nuevos |
| 2 | Traducir giro | Convierte "tiendita" o "estética" en clases SCIAN | Haiku | H10, H19 | H10 cerrado: 91 % en banco ciego; se integra en H19 |
| 3 | Consultar datos | Escribe y ejecuta SQL sobre las vistas autorizadas | Sonnet | H19 | Pendiente |
| 4 | Buscar metodología | Responde preguntas sobre el DENUE, el SCIAN y los indicadores con notas escritas | Sonnet | H19 | Pendiente |
| 5 | Construir escena | Devuelve un estado de escena que el backend valida | Sonnet | H09, H14, H19 | El contrato está hecho (H09); falta la herramienta |

### 1. Resolver lugar

- **Para qué sirve:** es la herramienta más crítica. Sin un lugar bien resuelto, ninguna cifra territorial es confiable.
- **Cómo funciona:** es determinista y no usa modelo de lenguaje. Lee `semantic.lugar` y un glosario de alias. Cuando no puede resolver, lo dice.
- **Qué devuelve:** un estado (`resuelto`, `grupo`, `ambiguo`, `sin_resultado` o `fuera_de_cdmx`), con confianza y una nota. Si hay relación espacial ("cerca de"), trae el ancla y el radio.
- **Dónde está:** `prototipos/03-resolver-lugar/` (`resolver_lugar.py`, `herramienta.py`, `glosario.json`).
- **Falta:** el respaldo con modelo ligero para los casos que el glosario no cubre, y probarla con usuarios reales (pasa a H19 y H11).

### 2. Traducir giro

- **Para qué sirve:** la base clasifica los giros con SCIAN, y la gente no habla así. Esta herramienta hace de intérprete.
- **Cómo funciona:** primero busca en un glosario CDMX escrito a mano; si el texto es un lugar, responde que no es giro; si no, saca 10 clases candidatas por significado con EmbeddingGemma (modelo local) y Haiku elige entre ellas o dice que ninguna. Si no alcanza confianza, lo dice.
- **Qué devuelve:** un estado (`resuelto`, `grupo`, `ambiguo`, `sin_resultado` o `no_es_giro`), las clases con código y nombre, la capa que resolvió, confianza y una nota.
- **Dónde está:** `traducir-giro/` (`traducir_giro.py`, `herramienta.py`, `glosario.json`). Ahí se queda hasta H19, cuando entra al backend junto con resolver lugar.
- **Resultado:** 91 % de acierto en 66 giros de un banco ciego y 100 % de rechazo de lo que no es giro (H10, 15 nov 2026).
- **Decidido (22 nov 2026):** modelo local (EmbeddingGemma), no Voyage AI. Los vectores de las clases van en archivo, no en pgvector: son 948 y caben en memoria.
- **Falta (H19):** cómo carga el modelo el backend en el VPS (1.2 GB por proceso), catálogo de clases por edición y leer la licencia de Gemma antes de publicar.

### 3. Consultar datos

- **Para qué sirve:** es la que produce las cifras.
- **Cómo funciona:** el modelo capaz escribe SQL. Antes de ejecutarlo, se valida con sqlglot: solo `SELECT` y solo tablas de `semantic`. Se ejecuta con el rol `pulso_analista`, de solo lectura y con 8 segundos por consulta.
- **Qué devuelve:** las filas, la consulta usada y la fecha de corte de la edición.
- **Reglas:** nunca consulta tablas crudas. Una cifra que no viene de una consulta no se escribe.
- **Validación del resultado:** revisa cifras implausibles, la versión SCIAN y el territorio antes de responder.

### 4. Buscar metodología

- **Para qué sirve:** contesta preguntas del tipo "¿qué cubre el DENUE?" o "¿cómo se calcula la rareza?", sin tocar la base de cifras.
- **Cómo funciona:** búsqueda sobre notas metodológicas, el catálogo SCIAN y la documentación de indicadores. Es el único caso donde se busca por significado sobre textos largos.
- **Qué necesita:** que existan las notas (H22, página de metodología) y los embeddings de esos textos.
- **Límite:** debe decir qué no cubre el DENUE, y no rellenar con suposiciones.

### 5. Construir escena

- **Para qué sirve:** la respuesta del Analista no es solo texto, también mueve la escena del portal.
- **Cómo funciona:** el modelo propone un estado de escena y el backend lo valida contra el contrato en tres niveles (estructura, referencias y coherencia). Si no valida, se le devuelve el error al modelo.
- **Qué necesita:** el contrato (H09, hecho), el catálogo de referencias exportado de `semantic` y el backend de validación (H14).
- **Regla:** el estado no lleva colores ni cifras escritas a mano; los colores los toma el motor de los tokens.

## Lo que rodea a las herramientas

Estas piezas no son herramientas que el modelo llame, pero sin ellas el Analista no es confiable:

| Pieza | Para qué | Hito |
|---|---|---|
| Banco de evaluación | Mínimo 20 preguntas con cifra esperada, consulta de referencia y escena esperada; corre en integración continua y reporta acierto por tipo | H11 |
| Caché de prompt | Reutiliza el esquema de vistas, el glosario y el catálogo SCIAN entre preguntas | H19 |
| Caché de intención | Dos preguntas con la misma intención comparten panel | H20 |
| Límites y presupuesto | Tope por IP, conversación y pregunta; Cloudflare Turnstile; modo degradado al llegar al presupuesto | H20 |
| Observabilidad | Langfuse autoalojado: preguntas, herramientas, SQL y costo | H20 |
| Persistencia de paneles y conversaciones | `app.panel` y `app.conversacion`, con identificador por contenido | H14 |

## Orden sugerido

1. **H10:** traducir giro (hecho el 22 nov 2026).
2. **H11:** banco de evaluación, para tener la vara de medir antes de construir el ciclo.
3. **H14:** validación y persistencia de paneles (habilita construir escena).
4. **H19:** orquestación con las cinco herramientas; debe superar el banco de H11.
5. **H20:** caché, límites y observabilidad.

## Criterio común de terminado

El Analista supera el banco de evaluación (H11) y **nunca escribe una cifra que no venga de una consulta**.

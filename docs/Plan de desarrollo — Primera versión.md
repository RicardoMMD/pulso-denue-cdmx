# Plan de desarrollo — Pulso DENUE CDMX, primera versión

Aprobado: 14 nov 2026 · Hitos y su estado: `docs/Seguimiento — Hitos del proyecto.md` · Decisiones: `docs/Pulso DENUE CDMX — Síntesis del proyecto.md`

## Contexto

La capa de datos y los tres prototipos están cerrados (H01–H06). El producto no tiene código: no existen `backend/`, `frontend/` ni `contenido/`. Faltan 20 hitos para lanzar (H07–H26). Este plan los ordena en seis etapas según sus dependencias, dice qué se reutiliza de lo que ya existe y cómo se comprueba cada etapa.

La pieza que desbloquea casi todo es el contrato de escena (H09): de él dependen el guion, el paquete estático, el backend, el motor y la vista exacta. Su spec está en borrador en `docs/changes/2026-11-08-contrato-escena/spec.md`, con el supuesto técnico ya probado (Pydantic → JSON Schema → Ajv → TypeScript funciona si el generador quita `discriminator.mapping`).

Hay una fecha externa: INEGI publica la edición 11/2026 el **25 de noviembre**. Hasta entonces se trabaja sobre la edición 2026-05.

## Decisiones tomadas el 14 nov 2026

Eran las cinco decisiones pendientes de la spec de H09:

1. En Corredores del Metro el radio es solo el parámetro de la escena; `territorio.radio_m` se rechaza ahí.
2. En Corredores la selección por giro solo atenúa puntos; las cifras no cambian (opción A, sin tocar dbt).
3. `radio_m` en el territorio solo para estación y conglomerado, no para calle.
4. Licencia MIT para el código, con atribución a OSM (ODbL) e INEGI en `referencias/LICENCIA.md`.
5. El repositorio público se crea solo con el "adelante" de Ricardo en ese momento, tras pasar gitleaks por el historial. Mientras tanto, CI se prueba en local con `make ci`.

## Estructura del repo al terminar

```
backend/      FastAPI + contratos (uv, Python 3.12–3.13, como pipeline/)
  contracts/  escena.py, catalogo.py, herencia.py, canonico.py, validar.py,
              vista_exacta.py, migraciones.py, referencias/, casos/
  contracts-ts/  tipos TS y validador Ajv generados
  app/        rutas /p/{id}, /c/{id}, validación, paneles
  analista/   orquestación, herramientas, caché, límites
frontend/     Vue 3 + Three.js + GSAP (nace del prototipo 2)
contenido/    historias YAML, recorridos JSON, metodología
paquete/      exportador del paquete estático por edición
```

## Etapas

### Etapa 0 · Poner la casa en orden (antes de escribir código)
- Commit de la gobernanza que hoy está sin rastrear: `CLAUDE.md`, `Makefile`, `.claude/`, el seguimiento y `docs/changes/`.
- Cerrar la spec de H09 con los supuestos de arriba y pasarla a "aceptada". Reflejar en la síntesis los cuatro puntos donde la spec se aparta de ella.
- Abrir el túnel y correr `make verify` para tener una línea base en verde.

### Etapa 1 · Contrato de escena (H09) — desbloquea todo lo demás
Orden de trabajo dentro del hito:
1. `backend/pyproject.toml` y los modelos `Estado` y `EstadoParcial` con las tres escenas (`escena.py`, `catalogo.py`).
2. `generar.py`: escribe `escena.v1.json` (sin `mapping`, con `title` en tipo y modo), los tipos TS y el validador Ajv.
3. `exportar_referencias.py`: lee `semantic` con el rol `pulso_analista` y escribe `referencias/2026-05.json`. Reutiliza la conexión de `prototipos/03-resolver-lugar/resolver_lugar.py` y las claves de `semantic.lugar`.
4. `validar.py` (tres niveles, errores con nivel, ruta, código y mensaje), `herencia.py` (seis reglas), `canonico.py` y su gemelo `canonico.ts`, `vista_exacta.py`, `migraciones.py`.
5. Banco de casos compartido en `contracts/casos/`, ejecutado por pytest y por `node --test`.
6. Una historia de ejemplo en `contenido/historias/` y el comando `validar-historias`.
7. `make contratos`, `make ci`, `make referencias`; `make verify` pasa a incluir `ci`. Workflow `.github/workflows/verificar.yml`.

**Terminado cuando:** se cumplen los ocho criterios de "Cómo sabremos que funcionó" del intent.

### Etapa 2 · Definición y datos (cuatro frentes en paralelo, tras la etapa 1)
- **H07 · Edición 11/2026** (a partir del 25 nov). Descargar, cargar a `raw` con `pipeline/cargar_raw.py`, `make build`, revisar reconciliación y bajas, volver a medir el prototipo 1 y regenerar las referencias. **Escribe en la base real: cada paso se pide a Ricardo en el momento.** Decide qué edición anterior se compara en el portal.
- **H08 · Sistema visual.** Paleta de 7 macrosectores probada con daltonismo y brillo aditivo, tipografía y parámetros de luz, aplicados sobre `prototipos/02-renderizador/src/main.js` sin perder rendimiento.
- **H10 · Traducir giro.** Glosario CDMX de giros, embeddings de clases SCIAN en pgvector y función `traducir_giro` con banco ciego de al menos 50 giros. Sigue el molde del prototipo 3 (`glosario.json`, `evaluar.py`, bancos ciegos). Aquí se decide el proveedor de embeddings.
- **H12 · Guion de "Vida comercial del Metro".** De 5 a 8 paneles en YAML, cada uno válido contra el contrato y con cifras de `semantic`.

### Etapa 3 · Cimientos de construcción (tras la etapa 1; H15 espera a H08)
- **H13 · Paquete estático y paridad.** Ampliar `prototipos/02-renderizador/exportar_paquete.py` con clase SCIAN, colonia y AGEB; agregados por unidad oficial, geometrías simplificadas y resultados de historias. La prueba de paridad compara paquete y conteo en navegador contra `semantic` y detiene la publicación ante cualquier diferencia.
- **H14 · Backend.** FastAPI con validación de estados, tablas `app.panel` y `app.conversacion` (DDL: se pide permiso), id por contenido sobre `canonico`, rutas `/p/{id}` y `/c/{id}`, resultados congelados y aviso de edición nueva.
- **H15 · Motor de escenas.** Vue 3 + Three.js con lienzo persistente, a partir del renderizador del prototipo 2; transiciones con GSAP según la matriz de coreografía de la síntesis; interrupciones, reposo y versión celular con agregados.
- **H11 · Banco de evaluación del Analista** (tras H10). Al menos 20 preguntas con cifra esperada, consulta de referencia y escena esperada; corre en CI.

### Etapa 4 · Producto visible
- **H17 · Vista exacta.** Cinco componentes 2D genéricos más la tabla, con cifra, fecha de corte y descarga. Sirven de respaldo sin WebGL2 y de lectura con lector de pantalla.
- **H16 · Las tres escenas.** Ciudad de luz, Corredores del Metro (línea y ranking) y Ciudades dentro de la ciudad (exterior e interior).
- **H18 · Recorridos de autor.** Formato JSON propio; El despertar, Tren de luz, Constelación de estaciones y Entrar al mercado. Cada plantilla se prueba con tres territorios extremos.
- **H22 · Página de metodología.** Puede empezar antes: solo depende de H03 y H04.

### Etapa 5 · El Analista
- **H19 · Orquestación.** Ciclo de herramientas con la API de Claude: un modelo ligero clasifica, resuelve lugares y traduce giros; uno mayor escribe SQL y redacta. Cinco herramientas: resolver lugar (ya definida en `prototipos/03-resolver-lugar/herramienta.py`), traducir giro (H10), consultar datos (SQL validado con sqlglot sobre `semantic`, rol `pulso_analista`), buscar metodología y construir escena (valida con el contrato). Debe superar el banco de H11. Se parte en dos (22 nov 2026): **H19a**, el Analista como librería, se trabaja junto con H11 y no espera a H14; **H19b**, la integración con la API y la persistencia de paneles, sí espera a H14.
- **H20 · Caché, límites y observabilidad.** Caché de intención, límites por IP y conversación, Turnstile, presupuesto con modo degradado y Langfuse.

### Etapa 6 · Contenido, calidad y lanzamiento
- **H21 · Historia navegable** con dirección por panel y cifras que pasan la paridad.
- **H23 · Accesibilidad** y **H24 · Rendimiento** (gama media Android, iOS y con brillo; define el umbral para cambiar a agregados).
- **H25 · Despliegue.** Docker detrás de Traefik, estáticos en CDN, respaldo diario y procedimiento de publicación de una edición. El despliegue a producción se pide en el momento.
- **H26 · Lanzamiento**, con la edición vigente más reciente.

## Rutas

Una ruta es una cadena de hitos que se puede trabajar de corrido, sin esperar a las demás, hasta llegar a un punto de cruce. Sirve para decidir en qué trabajar hoy y para ver qué se retrasa si una ruta se detiene. Definidas el 22 nov 2026 a partir de la columna "Depende de" del seguimiento.

### Las ocho rutas

| Ruta | Cadena | Estado | Qué entrega por sí sola |
|---|---|---|---|
| **Ciudad** (camino crítico) | `H05 ✅ H08 ✅ H09 ✅ → H15 + H13 → H16 → H18 → H21` | Sin empezar desde H15 | La historia "Vida comercial del Metro" navegable |
| **Analista** | `H10 ✅ → H11 + H19a → H19b → H20` | H11 y H19a, listos para empezar | Un Analista medido, con límites y panel compartible |
| **Datos** | `H07 → regeneraciones` | Espera a INEGI (25 nov) | La edición 11/2026 vigente, con referencias, catálogo y banco al día |
| **Backend** | `H09 ✅ → H14` | Sin empezar; pide permiso para DDL | Paneles con dirección estable (`/p/{id}`, `/c/{id}`) |
| **Lectura** | `H09 ✅ + H13 → H17 → H23` | Espera a H13 | Vista exacta 2D, respaldo sin WebGL2 y lectura con lector de pantalla |
| **Contenido** | `H03 ✅ H04 ✅ → H22` (y `H12 ✅ → H21`, que cierra en Ciudad) | H22 puede empezar ya | Página de metodología; el guion (H12) ya está hecho y espera a las escenas |
| **Salida** | `H13 + H14 → H25 → H26` | Espera a las demás | Despliegue y lanzamiento |
| **Diferida** | `H24, H27` | Fuera de la v1 | Rendimiento en dispositivos y segunda versión |

### Qué hay en cada ruta

**Ciudad.** Es el camino crítico: de ella depende el lanzamiento (H26).
- H15 y H13 se trabajan en paralelo; H16 espera a los dos.
- H17 (ruta Lectura) también cuelga de H13, pero no frena a H16.
- El riesgo mayor de calendario está en H15 y H16, el motor y las escenas. La salida es una prueba corta en el laboratorio antes de la spec completa: lienzo persistente, una transición con GSAP entre dos escenas y el mismo punto viajando entre las dos vistas.

**Analista.** Plan de la ruta en `docs/changes/2026-11-22-ruta-analista/plan.md`. Su primera etapa se trabaja como subproyecto aparte (`docs/changes/2026-11-22-h11-banco-analista/plan.md`).
- H11 y H19a van juntos, con línea base temprana y registro de experimentos.
- Solo H19b necesita algo de otra ruta: H14, de la ruta Backend.
- H20 no entra a la v1 sin H19b, pero sus partes sin panel (límites, presupuesto) se pueden adelantar.

**Datos.** Es corta pero tiene fecha externa.
- H07 pide permiso en cada escritura a la base real.
- Después de H07 se regeneran las referencias (`make referencias`), el catálogo y los vectores de traducir giro, el `esperado` del banco de H11 y la medición del prototipo 1.
- H13 conviene dejarlo después de H07 para no rehacer el paquete con la edición nueva, aunque el seguimiento no los encadena.

**Backend.** H14 es chico en dependencias (solo H09) pero pesado en permisos: crea `app.panel` y `app.conversacion` en la base real, así que el DDL se pide en el momento.

**Lectura.** H17 comparte con la ruta Ciudad los resultados del paquete (H13). H23 espera a H17 y también se prueba con las escenas de H16.

**Contenido.** H22 depende solo de H03 y H04, ambos hechos, así que se puede trabajar ahora sin esperar a H07. H21 es el cruce con la ruta Ciudad.

**Salida.** H25 necesita el paquete (H13) y el backend (H14). H26 reúne todo lo anterior, menos H24.

**Diferida.** H24 queda fuera de la v1 por decisión del 14 nov 2026, y H27 es la segunda versión.

### Puntos de cruce

| Hito | Une | Por qué importa |
|---|---|---|
| **H13** | Ciudad, Lectura, Salida y Datos | Es el hito más compartido: sin paquete no hay escenas, vista exacta ni despliegue. Es el siguiente cuello de botella tras el contrato |
| **H14** | Backend, Analista y Salida | Su retraso frena H19b y H25, pero no la evaluación del Analista |
| **H07** | Datos, Analista y Ciudad | Cambia las cifras: el `esperado` de H11, las referencias del contrato y el paquete de H13 |
| **H21** | Ciudad y Contenido | La historia necesita las escenas (H16) y los recorridos (H18) |
| **H26** | Todas | Cierra cuando todas terminan, salvo la Diferida |

### Qué se puede trabajar hoy, por ruta

| Ruta | Se puede hacer ahora | Espera a |
|---|---|---|
| Ciudad | La prueba corta del motor en el laboratorio; la spec de H15 y H13 | La edición 11/2026, para el paquete definitivo |
| Analista | El banco y el calificador (H11); el Analista con línea base (H19a) | H14, solo para H19b |
| Datos | El plan de H07, ya escrito (`docs/changes/2026-11-22-h07-carga-2026-11/plan.md`) | INEGI, el 25 nov |
| Backend | Diseño de H14 (spec y modelo de la tabla) | Permiso de DDL para crearlas |
| Lectura | Los componentes 2D con cifras del contrato | H13 para los datos reales |
| Contenido | La página de metodología (H22) | Nada |

### Cómo elegir en qué trabajar

- **Si algo bloquea a varias rutas, va primero:** H07 el 25 nov, y después H13.
- **Si no hay nada que bloquee, se avanza la ruta Ciudad**, porque es la que fija la fecha del lanzamiento.
- **Las rutas Analista y Contenido son las que se pueden trabajar sin esperar a nadie:** sirven para llenar los huecos mientras llegan los permisos o la edición.
- **El riesgo de calidad es H24** (gama media y brillo), que quedó fuera de la v1. Una prueba rápida del prototipo 2 con brillo, ahora que existe H08, no obliga a retomarlo.

## Cómo se trabaja cada hito

- Hitos grandes (H09, H13, H14, H15, H19): `intent.md → spec.md → plan.md` en `docs/changes/<fecha>-<slug>/`, con aceptación de Ricardo entre etapas. Los demás, con un plan breve.
- Al cerrar un hito: marcarlo en el seguimiento y registrar el resultado en la síntesis.
- Nada que escriba en la base (`make build`, cargas, DDL) sin pedirlo en el momento.

## Verificación

- **Cada hito:** `make verify` en verde y la salida a la vista. Desde la etapa 1 incluye las pruebas del contrato y la validación de historias.
- **Etapa 1:** banco de casos con el mismo veredicto en Python y Node; bytes canónicos idénticos; una historia inválida deja `make ci` en rojo.
- **Etapa 3:** prueba de paridad del paquete contra `semantic`; guardar un panel dos veces devuelve el mismo id.
- **Etapa 4:** cada escena probada en navegador real y leída completa con lector de pantalla; mediciones de FPS guardadas en el repo.
- **Etapa 5:** acierto por tipo de pregunta en el banco de H11; ninguna cifra en una respuesta sin consulta que la respalde.
- **Lanzamiento:** publicar una edición siguiendo solo el procedimiento documentado.

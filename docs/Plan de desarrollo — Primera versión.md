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
- **H19 · Orquestación.** Ciclo de herramientas con la API de Claude: un modelo ligero clasifica, resuelve lugares y traduce giros; uno mayor escribe SQL y redacta. Cinco herramientas: resolver lugar (ya definida en `prototipos/03-resolver-lugar/herramienta.py`), traducir giro (H10), consultar datos (SQL validado con sqlglot sobre `semantic`, rol `pulso_analista`), buscar metodología y construir escena (valida con el contrato). Debe superar el banco de H11.
- **H20 · Caché, límites y observabilidad.** Caché de intención, límites por IP y conversación, Turnstile, presupuesto con modo degradado y Langfuse.

### Etapa 6 · Contenido, calidad y lanzamiento
- **H21 · Historia navegable** con dirección por panel y cifras que pasan la paridad.
- **H23 · Accesibilidad** y **H24 · Rendimiento** (gama media Android, iOS y con brillo; define el umbral para cambiar a agregados).
- **H25 · Despliegue.** Docker detrás de Traefik, estáticos en CDN, respaldo diario y procedimiento de publicación de una edición. El despliegue a producción se pide en el momento.
- **H26 · Lanzamiento**, con la edición vigente más reciente.

## Camino crítico

`H09 → H13 + H15 → H16 → H21 → H26`. El Analista (`H10 → H11 → H19 → H20`) corre en paralelo y solo necesita H14 del resto. El riesgo mayor de calendario es H15–H16 (motor y escenas); el de calidad, H24 en gama media, que conviene adelantar con una prueba del prototipo 2 con brillo en cuanto exista H08.

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

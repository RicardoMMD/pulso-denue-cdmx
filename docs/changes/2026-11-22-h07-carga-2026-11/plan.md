# Plan: carga de la edición DENUE 11/2026 (H07)

Estado: propuesto (22 nov 2026), sin ejecutar · Ref: H07 en `docs/Seguimiento — Hitos del proyecto.md` · Antecedente: `data/raw/MANIFEST.md`

## Qué se sabe hoy

- **INEGI todavía no publica la 11/2026.** El 22 nov 2026, en la descarga masiva (`https://www.inegi.org.mx/app/descarga/?ti=6`), filtrando por Ciudad de México y DENUE, la última edición listada es **05/2026**. La fecha de publicación prevista es el **25 nov 2026**.
- **La descarga se hace en la página de INEGI, no con una URL fija.** El zip `denue_09_csv.zip` sirve solo la edición vigente: cuando salga la 11/2026, su contenido cambia. Por eso `data/raw/MANIFEST.md` guarda el hash de cada zip.
- **Ediciones disponibles para comparar** (listado de la descarga masiva, CDMX): 2024/05, 2024/11, 2025/05 y 2026/05. No aparece la 11/2025, así que la edición previa a la 11/2026 es la 05/2026.
- **Las ediciones anteriores se bajaron a mano**, y el formato es el mismo (ISO-8859-1, 42 columnas). Playwright sirve para la descarga y deja el mismo zip, con su hash.

## Qué se hace, en orden

### Paso 1 · Descarga (25 nov o después; con Playwright)
- Abrir la descarga masiva, filtrar por Ciudad de México y DENUE, y buscar la fila con periodo **11/2026**.
- Bajar el zip de CSV. Guardarlo en `data/raw/` (no versionado), registrar su SHA-256 y sus filas en `data/raw/MANIFEST.md`, y verificar que la edición coincide con lo que dice la página.
- La descarga no toca la base. Si la página no muestra la 11/2026 al momento de correr el paso, se detiene y se avisa; no se reintenta en bucle.

### Paso 2 · Revisión del archivo (sin base)
- Número de filas y de ids duplicados; todas las filas con coordenadas; encoding y 42 columnas.
- Comparar el conteo por alcaldía y por sector contra 05/2026. Un cambio fuerte se reporta antes de seguir.

### Paso 3 · Carga a `raw` (solo con permiso)
- `cargar_raw.py 2026-11 <csv> 2026-11-25`. Escribe en la base real, así que se pide en el momento.

### Paso 4 · Reconstrucción `staging → core → semantic` (solo con permiso)
- `make build` sobre la base real, también con permiso en el momento.
- Revisar la reconciliación: ids nuevos (`id`), ids que volvieron (`id_salto`), reúso y bajas del SCD tipo 2. Se compara contra las transiciones de 05/2025 → 05/2026, que sirven de referencia de lo plausible.

### Paso 5 · Regeneraciones que dependen de la edición
- `backend/contracts/referencias/2026-11.json` (`make referencias EDICION=2026-11`, solo lectura).
- Catálogo de traducir giro y sus vectores (`traducir-giro/datos/clases.json` y `vectorizar.py`), porque el texto de cada clase usa palabras de los nombres comerciales de la edición.
- Volver a medir el prototipo 1 (compuerta de conglomerados) con la edición nueva.

### Paso 6 · Cierre
- Marcar H07 en el seguimiento y registrar el resultado en la síntesis.
- `make verify` con la salida a la vista.

## Decisiones que toma Ricardo

| # | Decisión | Propuesta |
|---|---|---|
| D1 | Edición con la que el portal compara la 11/2026 | **05/2026**: es la edición inmediata anterior (la 11/2025 no existe en el listado) |
| D2 | Cuándo se hace la carga a la base real | Después de la revisión del paso 2, con permiso explícito |
| D3 | Qué se hace si la edición se retrasa | Se espera; H07 no tiene fecha de entrega sin la edición |

## Terminado cuando

- La 11/2026 queda cargada como vigente, con su hash en el manifiesto.
- La tasa de ids nuevos y las bajas son plausibles frente a 05/2025 → 05/2026.
- Las regeneraciones del paso 5 están al día, y `make verify` está en verde.

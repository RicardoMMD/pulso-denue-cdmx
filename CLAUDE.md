# Pulso DENUE CDMX

Portal que muestra los ~460 mil establecimientos del DENUE de CDMX como una "ciudad de luz" en WebGL, con historias, explorador y un Analista (Claude) que responde con cifras de la base. La fuente de las decisiones es `docs/Pulso DENUE CDMX — Síntesis del proyecto.md`; el avance, `docs/Seguimiento — Hitos del proyecto.md` (hitos H01–H27).

## Arquitectura
- **Base:** PostgreSQL 18 + PostGIS + pgvector en el VPS (`localhost:5433`), una sola base `pulso_denue`. Desde aquí, por túnel: `ssh -f -N -L 55432:localhost:5433 vps`.
- **pipeline/** (Python, `uv`): descarga y carga fuentes a `raw`. **dbt/**: `raw → staging → core → semantic`.
- **semantic** es la única superficie del Analista y de las cifras publicadas. Rol `pulso_analista`: solo lectura, 8 s por consulta.
- **prototipos/**: 02 renderizador (Vite + Three.js), 03 resolver lugar (Python determinista).
- **laboratorio/**: laboratorio visual (Vite + Three.js). Página para ver las propuestas implementadas y compararlas; `cd laboratorio && npm run dev`. Lee `diseno/generado/` y los datos de `prototipos/02-renderizador/public/datos/`.
- **diseno/**: sistema visual (H08). `tokens.json` es la fuente de la paleta por macrosector (oscura y clara), la luz y la tipografía; `generar.mjs` produce `generado/tokens.js` (motor) y `generado/tokens.css` (interfaz y vista 2D).
- **backend/** (Python, `uv`): `contracts/` es el contrato de escena (H09): modelos Pydantic v2, validación en tres niveles, herencia, forma canónica y migraciones. `contracts-ts/` es su parte del navegador (Ajv, tipos TS, forma canónica espejo). **contenido/historias/**: historias en YAML. No necesitan la base: el nivel 2 usa `contracts/referencias/<edicion>.json`.

## Comandos
| Comando | Qué hace | Salida esperada |
|---|---|---|
| `make verify` | `ci` + túnel + `dbt test` (solo lectura, ~75 s) | `verify: OK`, exit 0 |
| `make ci` | Lo que corre GitHub Actions, sin base: `check` + `contratos` (~4 s) | `ci: OK` |
| `make diseno` | Pruebas de los tokens del sistema visual: contraste, macrosectores y generado al día | `diseno: OK` |
| `make contratos` | pytest, pruebas de Node, validación de historias y archivos generados al día | `contratos: OK` |
| `make referencias` | Re-exporta el catálogo de referencias desde `semantic` (solo lectura, necesita túnel; `EDICION=2026-05`) | `escrito .../2026-05.json` |
| `make check` | Sintaxis Python/JS y `dbt parse`, sin base | `check: OK` |
| `make build` | **Reconstruye la base real** (`dbt build`) | `Completed successfully` |
| `make eval-lugar` | Banco del prototipo 3; reescribe `resultados.md` | tabla de aciertos |

## Convenciones
- Todo en español: código, nombres de modelos y columnas, docs y commits. Docs en prosa llana, sin jerga.
- Modelos `semantic`: claves naturales, sin llaves sustitutas; cada tabla y columna documentada en `_semantic.yml` (se escribe como `COMMENT`). Una tabla nueva lleva pruebas de grano y paridad.
- Las cifras de historias, fichas y del Analista salen de `semantic`, nunca escritas a mano.
- Secretos solo en `.env` (no versionado). No copiar credenciales a archivos, logs ni chat.
- No se editan a mano `backend/contracts/escena.v1.json`, `backend/contracts-ts/escena.v1.d.ts` ni `validar-estructura.js`: se generan con `cd backend && uv run python -m contracts.generar`, y `make contratos` falla si están desactualizados. Un cambio en el contrato empieza en `backend/contracts/escena.py` y en `catalogo.py`.
- No se editan a mano `diseno/generado/*`: salen de `diseno/tokens.json` con `node diseno/generar.mjs`, y `make diseno` falla si están desactualizados. Ningún color ni parámetro de luz va escrito a mano en el código: se lee de los tokens. El color no entra al contrato ni a la base.
- Cambiar la forma canónica (`canonico.py`/`canonico.ts`) cambia los ids de los paneles: es un cambio de versión del contrato, con migración. Los bancos `backend/contracts/casos/` se revisan a mano, no se regeneran para que una prueba pase.
- Al cerrar un hito: marcarlo en el seguimiento y registrar el resultado en la síntesis.
- Todo cambio o hito con algo que ver se entrega con un **repaso desde el laboratorio visual** (`laboratorio/`): qué abrir, qué comparar, qué decidir. Si el cambio es visual, se agrega o actualiza la comparación ahí; no basta describirlo en texto.

## Decisiones que no se reabren
- La privacidad no es restricción: se muestran establecimientos individuales con nombre.
- El modelo de datos completo (estrella + copo, multiedición, SCD tipo 2) se queda; no proponer simplificarlo.

## Cuidado
- Solo hay una base y es la real: no correr `dbt build`, `dbt seed`, cargas del pipeline ni DDL sin que el usuario lo pida en ese momento. Para verificar, `make verify`. Lo respalda un hook (`.claude/hooks/deploy-gate.sh` + `.claude/deploy-patterns`) que pide confirmación; un `python -` que escribe con psycopg no lo detecta.
- `evaluar.py` termina en 0 aunque falle casos y reescribe archivos versionados: no sirve como prueba automática.
- El cluster PostgreSQL 16 del mismo VPS (puerto 5432) es de otros proyectos: no tocarlo.

## Verificación
Antes de dar algo por terminado: `make verify` y mostrar la salida. Si cambiaste modelos dbt, lo que falta es `make build` sobre la base real: pídelo, no lo corras por tu cuenta.

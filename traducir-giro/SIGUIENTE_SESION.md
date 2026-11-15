# Traducir giro — arranque de la siguiente sesión

Escrito el 15 nov 2026. Lee primero `README.md` (planteamiento y criterios de logro) y `../docs/changes/2026-11-15-traducir-giro/plan.md` (plan de H10; el README manda donde difieran).

## Estado
- Solo hay documentos. No hay código, ni modelos descargados, ni nada en la base.
- Rama de trabajo: `traducir-giro`, desde `main`. El grafo de graphify está actualizado al 15 nov (solo código; los `.md` nuevos no están en él).

## Decisiones tomadas
- Se comparan tres modelos locales: Qwen3-Embedding-0.6B, BGE-M3 y EmbeddingGemma (línea base opcional: multilingual-e5-small). Jina v5 queda fuera por licencia no comercial.
- Todo en local; nada de pgvector ni de la base real hasta que haya un modelo ganador.
- Jev (modelo "Sistema Uno") descartado: elige entre 255 opciones como máximo y hay unas 950 clases.
- Los bancos se escriben antes de correr modelos; el ciego se corre una sola vez.

## Pendiente de Ricardo (confirmar antes de correr el banco ciego)
1. Umbrales C1–C5 del README (85 %, 70 %, 80 % con 5 % de pérdida, 2 GB y 200 ms).
2. Dónde se construye el resto de H10 (glosario, función completa, pgvector): en este directorio o en el proyecto principal.
3. EmbeddingGemma puede pedir aceptar los términos de Google en Hugging Face con su cuenta (por verificar).

## Primeros pasos
1. Crear `pyproject.toml` propio con `uv` (versiones fijas; no mezclar con `pipeline/` ni `backend/`).
2. Exportar el catálogo desde `semantic.actividad` a `datos/clases.json` (solo lectura, necesita túnel: `ssh -f -N -L 55432:localhost:5433 vps`).
3. Escribir los bancos de ajuste y ciego, y verificar a mano las clases esperadas.
4. Línea base de los tres modelos sobre el banco de ajuste.

## Cuidado
- Pedir permiso antes de descargar cada modelo (nombre, fuente y tamaño).
- No escribir en la base. No copiar llaves ni credenciales.
- Al terminar: repaso en `laboratorio/` (`giros.html`) y `make verify` a la vista.

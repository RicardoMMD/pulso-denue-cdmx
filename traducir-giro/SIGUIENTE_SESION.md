# Traducir giro — arranque de la siguiente sesión

Actualizado el 15 nov 2026. Lee primero `README.md`: la sección "Resultados" resume todo lo medido.

## Estado
- Comparación de embeddings cerrada: ningún modelo cumplió solo en el banco ciego. Se eligió EmbeddingGemma (texto `palabras`) como generador de candidatos. Qwen3 quedó fuera por costo y acierto; BGE-M3, por peso.
- Herramienta completa construida en `traducir_giro.py`: glosario, lugar, 10 candidatos de Gemma y `claude-haiku-5-5` que elige. En ajuste da 99 % de acierto, inflado porque el glosario salió de ese banco.
- Segundo banco ciego escrito por un agente aislado (`bancos/ciego.json`, 90 casos). **No se ha corrido.**
- Nada se ha escrito en la base. Modelos y vectores están en `modelos/` y `vectores/`, sin versionar.

## Pendiente de Ricardo
1. Revisar las clases aceptadas de `bancos/ciego.json`. El agente señaló dudas en los casos 10, 16, 19, 30 y 43 (numerados desde 1). Quien afina la herramienta no debe abrir ese archivo.
2. Dar la orden de correrlo: `make herramienta-ciego` (una sola vez; usa la llave de Anthropic del `.env`).
3. Decidir dónde vive la herramienta en el proyecto principal y la decisión D3 del plan (pgvector o archivo).

## Después del ciego
- Si cumple C1–C3: registrar el resultado en la síntesis, actualizar `docs/Herramientas del Analista.md`, marcar H10 si también se resolvió D3, y abrir el pull request.
- Si no cumple: sus fallos pasan al ajuste (y al glosario los de palabra de la calle), y se escribe un tercer banco ciego con otro agente aislado.

## Cuidado
- Para regenerar vectores: `uv run python vectorizar.py gemma --variante palabras` (la herramienta los necesita).
- Los modelos se cargan en fp32 a propósito (ver `comun.cargar_modelo`).
- No escribir en la base. No copiar llaves ni credenciales.
- Repaso en `laboratorio/giros.html` y `make verify` a la vista antes de dar algo por terminado.

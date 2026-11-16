# Traducir giro — arranque de la siguiente sesión

Actualizado el 15 nov 2026. Lee primero `README.md`: la sección "Resultados" resume todo lo medido.

## Estado
- Los embeddings solos no cumplieron en el primer banco ciego. Se eligió EmbeddingGemma (texto `palabras`) como generador de candidatos. Qwen3 quedó fuera por costo y acierto; BGE-M3, por peso.
- La herramienta completa (`traducir_giro.py`: glosario, lugar, 10 candidatos de Gemma y `claude-haiku-5-5`) **cumple C1–C3 en el segundo banco ciego**: 91 % de acierto, 100 % de rechazo y 3 % de giros perdidos. Ese banco ya está usado: `resultados/herramienta/ciego.json` lo marca y el script no lo repite.
- Nada se ha escrito en la base. Modelos y vectores están en `modelos/` y `vectores/`, sin versionar.

## Pendiente de Ricardo
1. Decidir si H10 se da por cerrado. El criterio del seguimiento ("al menos 50 giros coloquiales con acierto medido en un banco ciego") se cumple: 66 giros, 91 %. Faltan dos decisiones de integración:
   - Dónde vive la herramienta en el proyecto principal (hoy está aquí, con el modelo y sus dependencias) y cómo la carga el backend en el VPS.
   - Decisión D3 del plan: vectores en pgvector (escribir en la base real, solo con permiso) o desde archivo hasta H19.
2. Licencia de Gemma: se deja para después (decisión del 15 nov 2026). La RAM del VPS alcanza para el modelo.

## Correcciones ya aplicadas (después de medir)
- Los 6 fallos del segundo ciego se corrigieron: glosario ampliado (130 entradas), parecido de escritura respaldado por embeddings o confirmado por Haiku, y la regla de reparación en el prompt (versión 2). Detalle en el README.
- En ajuste: 99 % de acierto. Ese número no se compara con el 91 % del ciego; la versión corregida necesita su propio banco ciego (propuesto para H11).
- Pendiente menor: «cerca del metro» y «a dos cuadras del metro» salen `ambiguo` con transporte; «Bosque de Chapultepec» no lo reconoce el detector de lugares (no tiene parques).

## Cuidado
- Para regenerar vectores: `uv run python vectorizar.py gemma --variante palabras` (la herramienta los necesita).
- Los modelos se cargan en fp32 a propósito (ver `comun.cargar_modelo`).
- No escribir en la base. No copiar llaves ni credenciales.
- Repaso en `laboratorio/giros.html` y `make verify` a la vista antes de dar algo por terminado.

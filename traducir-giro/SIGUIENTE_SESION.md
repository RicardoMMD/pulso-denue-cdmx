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
2. Leer la licencia de Gemma (condiciones de uso) antes de producción.

## Mejoras conocidas (cualquier cambio exige un banco ciego nuevo para afirmar un número)
- El parecido de escritura del glosario confunde palabras distintas: «pastelería» salió como papelería.
- Palabras que faltan en el glosario: talachería, maquinitas, ropa de paca, materias primas.
- Haiku eligió fabricación en vez de reparación en «donde componen bicicletas».
- La herramienta es generosa con los grupos (73 % de respuestas limpias).

## Cuidado
- Para regenerar vectores: `uv run python vectorizar.py gemma --variante palabras` (la herramienta los necesita).
- Los modelos se cargan en fp32 a propósito (ver `comun.cargar_modelo`).
- No escribir en la base. No copiar llaves ni credenciales.
- Repaso en `laboratorio/giros.html` y `make verify` a la vista antes de dar algo por terminado.

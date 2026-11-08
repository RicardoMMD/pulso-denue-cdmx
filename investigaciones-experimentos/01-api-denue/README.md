# 01 — Exploración de la API DENUE

**Pregunta:** ¿qué ofrece la API de INEGI frente a la descarga masiva, y sirve para algo en el pipeline?

## Cómo correrlo

Requiere `DENUE_API_TOKEN` en el `.env` de la raíz (token gratuito de INEGI).

```bash
cd investigaciones-experimentos/01-api-denue
python3 explorar.py
```

Las respuestas se guardan en `cache/` (ignorada por git) para no repetir llamadas.

## Hallazgos

- **La API sirve la misma edición que el CSV.** `Cuantificar` suma 462 732 establecimientos en CDMX, igual que las filas del CSV 05/2026.
- **Cuantificar** devuelve conteos por clave SCIAN de 2, 3 y 4 dígitos en una sola llamada. Útil para validar la carga: los conteos por sector deben coincidir con `core`.
- **Buscar** (radio en metros desde un punto) y **BuscarEntidad** (paginado por filas) devuelven 22 campos. Buscar por nombre trae pocos resultados: "fonda" a 500 m del Zócalo da 2.
- **Ficha** devuelve un establecimiento por id.
- **Diferencias con el CSV:** la API trae `CLEE` y `Id`, pero no trae `cve_ent/cve_mun/cve_loc/ageb/manzana` ni `fecha_alta`; la ubicación viene como texto. Por eso no reemplaza al CSV para el modelo de datos.

## Uso previsto

La carga masiva sigue siendo el CSV. La API queda para validación cruzada y para fichas puntuales.

## Ediciones anteriores, límites y filtros (segunda ronda)

- **La API no tiene parámetro de edición.** La documentación lista siete métodos y ninguno acepta versión. La ruta `v2` no existe ("No hay resultados"). La API solo sirve la edición vigente, así que **no resuelve la comparación**: la edición anterior sigue pendiente (ver la síntesis).
- **Paginación generosa.** `BuscarEntidad` devolvió 20 000 filas (12 MB) en una sola llamada. La documentación no declara tope de filas ni cuota; el único límite documentado es 5 000 m de radio en `Buscar`.
- **Filtro por AGEB y manzana.** `BuscarAreaAct` con entidad 09, municipio 017, AGEB 1204 y manzana 001 devolvió 3 establecimientos, entre ellos el "ACUARIO AQUAVIRTUAL" que aparece en esa manzana en el CSV. Sirve para comprobar la carga manzana por manzana.

## Pendiente de explorar

- Cuota real de llamadas (no documentada): medir con ráfagas.
- Si `Cuantificar` acepta estrato y área menor al estado (municipio, AGEB), para validar por colonia.

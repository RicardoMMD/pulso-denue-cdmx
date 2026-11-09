# Prototipo 2 — renderizador sin mapa base

Ciudad de luz con los 462 729 establecimientos de CDMX (DENUE 2026-05), un solo contexto WebGL2, fondo dibujado desde datos propios (siluetas de alcaldías) y paleta provisional de 7 macrosectores.

## Cómo correrlo

```bash
# 1. Paquete de datos (túnel SSH abierto y .env cargado), una vez por edición
cd pipeline && set -a && . ../.env && set +a
uv run --with numpy python ../prototipos/02-renderizador/exportar_paquete.py 2026-05

# 2. Servidor (escucha en la red local)
cd ../prototipos/02-renderizador && npm install && npm run dev -- --port 5174
```

Parámetros de URL: `bench=1` (benchmark automático), `bloom=0|1`, `dpr=<número>`, `pts=<0–1>` (fracción de puntos).

## Prueba en celular

1. Celular y computadora en la misma red wifi. Abrir `http://<IP de la computadora>:5174/?bench=1`.
2. Esperar ~15 s con la pantalla encendida y sin tocarla. El resultado aparece en pantalla y se guarda solo en `resultados/bench-*.json`.
3. Repetir con `&bloom=1` para medir el costo del brillo.

## Qué se mide y por qué

- **GPU por cuadro** (`EXT_disjoint_timer_query_webgl2`): costo real del dibujo; es la cifra que cuenta.
- **FPS y p95 del cuadro**: dependen de cómo el navegador presente los cuadros. En el Chrome automatizado de desarrollo un lienzo WebGL vacío daba 5 FPS, así que ahí esas cifras no son válidas; en un dispositivo real sí.
- El recorrido del benchmark (12 s) incluye el encendido inicial, acercamiento oblicuo, órbita y regreso, para estresar el tamaño de punto.

## Paquete de datos (`public/datos/`, no se versiona: se regenera con `exportar_paquete.py`)

`puntos.bin` (3.2 MB): x e y en Uint16 a 1 m desde (minx, miny), macrosector, estrato y alcaldía en Uint8 (7 bytes por punto). `fondo.json`: alcaldías simplificadas a 40 m. `meta.json`: conteos, edición y fecha de corte. Posiciones en metros locales (UTM 14N con origen en el centro).

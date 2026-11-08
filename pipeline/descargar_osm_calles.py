"""Descarga las calles de OpenStreetMap para el rectángulo de CDMX (Overpass API), por mosaicos.

Guarda un JSON por mosaico en data/raw/externas/osm/. Los ways que cruzan mosaicos se repiten; se
deduplican al cargar. Uso: python3 descargar_osm_calles.py
"""
import json, pathlib, subprocess, time, urllib.parse

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "data" / "raw" / "externas" / "osm"
SUR, OESTE, NORTE, ESTE = 19.04, -99.37, 19.60, -98.94
FILAS, COLS = 4, 4
TIPOS = ("motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|pedestrian|"
         "service|motorway_link|trunk_link|primary_link|secondary_link|tertiary_link")

SALIDA.mkdir(parents=True, exist_ok=True)
for i in range(FILAS):
    for j in range(COLS):
        s = SUR + (NORTE - SUR) * i / FILAS
        n = SUR + (NORTE - SUR) * (i + 1) / FILAS
        o = OESTE + (ESTE - OESTE) * j / COLS
        e = OESTE + (ESTE - OESTE) * (j + 1) / COLS
        destino = SALIDA / f"calles_{i}_{j}.json"
        if destino.exists() and destino.stat().st_size > 1000:
            continue
        q = f'[out:json][timeout:180];way["highway"~"^({TIPOS})$"]({s:.5f},{o:.5f},{n:.5f},{e:.5f});out geom;'
        for intento in range(4):
            r = subprocess.run(
                ["curl", "-s", "-m", "240", "-A", "pulso-denue/0.1", "--data-urlencode", f"data={q}",
                 "https://overpass-api.de/api/interpreter", "-o", str(destino)], capture_output=True)
            try:
                d = json.loads(destino.read_text())
                print(f"mosaico {i},{j}: {len(d['elements'])} ways", flush=True)
                break
            except Exception:
                destino.unlink(missing_ok=True)
                print(f"mosaico {i},{j}: reintento {intento + 1}", flush=True)
                time.sleep(30 * (intento + 1))
        else:
            raise SystemExit(f"mosaico {i},{j} falló")
        time.sleep(10)

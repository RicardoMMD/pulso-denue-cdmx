"""Exporta el paquete estático mínimo del prototipo 2 (edición base) desde la base `pulso_denue`.

Salida en public/datos/:
  puntos.bin   n × (x Uint16, y Uint16) | n × macrosector Uint8 | n × estrato Uint8 | n × alcaldía Uint8
               x, y en metros desde (minx, miny); proyección local (UTM 14N con origen en el centro).
  meta.json    n, minx, miny, edición, fecha de corte, macrosectores, alcaldías
  fondo.json   alcaldías simplificadas (anillos en metros locales) para el fondo propio

Uso (túnel abierto y .env cargado):  uv run --project ../../pipeline python exportar_paquete.py [edición]
"""
import json, os, sys
from pathlib import Path
import numpy as np
import psycopg

ED = sys.argv[1] if len(sys.argv) > 1 else "2026-05"
OUT = Path(__file__).parent / "public" / "datos"
OUT.mkdir(parents=True, exist_ok=True)

c = psycopg.connect(host=os.environ["PGHOST"], port=os.environ["PGPORT"], dbname=os.environ["PGDATABASE"],
                    user=os.environ["PULSO_OWNER_USER"], password=os.environ["PULSO_OWNER_PASSWORD"])

ed = c.execute("select sk_edicion, fecha_corte from core.dim_edicion where edicion=%s", (ED,)).fetchone()
rows = c.execute("""
    select f.x_m, f.y_m, a.sk_macrosector, f.sk_estrato, u.sk_alcaldia
    from core.fact_establecimiento f
    join core.dim_actividad a using (sk_actividad)
    join core.dim_ubicacion u using (sk_ubicacion)
    where f.sk_edicion = %s
    order by f.id_denue""", (ed[0],)).fetchall()
arr = np.array(rows, dtype=np.float64)
n = len(arr)
minx, miny = float(np.floor(arr[:, 0].min())), float(np.floor(arr[:, 1].min()))
qx = np.round(arr[:, 0] - minx).astype(np.uint16)
qy = np.round(arr[:, 1] - miny).astype(np.uint16)
assert (arr[:, 0] - minx).max() < 65535 and (arr[:, 1] - miny).max() < 65535
macro = arr[:, 2].astype(np.uint8)
estrato = arr[:, 3].astype(np.uint8)
alc = arr[:, 4].astype(np.uint8)
with open(OUT / "puntos.bin", "wb") as f:
    for a in (qx, qy, macro, estrato, alc):
        f.write(a.tobytes())

# origen local: UTM absoluto = local + origen (se deduce de un punto)
ox, oy = c.execute("""
    select st_x(st_transform(geom::geometry, 32614)) - x_m, st_y(st_transform(geom::geometry, 32614)) - y_m
    from core.fact_establecimiento where sk_edicion=%s limit 1""", (ed[0],)).fetchone()

alcs = c.execute("select sk_alcaldia, nombre_alcaldia from core.dim_alcaldia order by 1").fetchall()
macros = c.execute("select sk_macrosector, nombre_macrosector from core.dim_macrosector order by orden").fetchall()
fondo = []
for sk, nombre in alcs:
    g = c.execute("select st_asgeojson(st_simplifypreservetopology(geom_utm, 40), 1) from core.dim_alcaldia where sk_alcaldia=%s", (sk,)).fetchone()[0]
    g = json.loads(g)
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    rings = [[[round(float(x) - float(ox) - minx), round(float(y) - float(oy) - miny)] for x, y in p[0]] for p in polys]
    fondo.append({"id": sk, "nombre": nombre, "anillos": rings})
(OUT / "fondo.json").write_text(json.dumps(fondo, separators=(",", ":")))
(OUT / "meta.json").write_text(json.dumps({
    "n": n, "minx": minx, "miny": miny, "w": int(qx.max()), "h": int(qy.max()), "edicion": ED,
    "fecha_corte": str(ed[1]), "macrosectores": [{"id": i, "nombre": nm} for i, nm in macros],
    "alcaldias": [{"id": i, "nombre": nm} for i, nm in alcs]}, ensure_ascii=False))
print(n, "puntos;", (OUT / "puntos.bin").stat().st_size, "bytes;", "origen", ox, oy)

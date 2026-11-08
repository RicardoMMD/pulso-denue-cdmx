"""Carga las calles de OpenStreetMap (descargar_osm_calles.py) a raw.osm_calles.

Una fila por way, deduplicado entre mosaicos. Se conserva la lista de nodos para poder cortar
las calles en cuadras (en dbt) y todas las etiquetas como jsonb.
Uso: uv run python cargar_osm_calles.py
"""
import glob, hashlib, io, json, os
import psycopg
from cargar_raw import RAIZ, env

DDL = """
DROP TABLE IF EXISTS raw.osm_calles;
CREATE TABLE raw.osm_calles (
  osm_id bigint PRIMARY KEY,
  highway text,
  nombre text,
  etiquetas jsonb,
  nodos bigint[],
  geom geometry(linestring, 4326)
);
"""


def main():
    env()
    ways = {}
    archivos = sorted(glob.glob(str(RAIZ / "data/raw/externas/osm/calles_*.json")))
    for a in archivos:
        for e in json.load(open(a))["elements"]:
            if e["type"] == "way" and e.get("geometry"):
                ways[e["id"]] = e
    print(f"{len(archivos)} mosaicos, {len(ways)} ways únicos")
    conn = psycopg.connect(
        host=os.environ["PGHOST"], port=os.environ["PGPORT"], dbname=os.environ["PGDATABASE"],
        user=os.environ["PULSO_OWNER_USER"], password=os.environ["PULSO_OWNER_PASSWORD"])
    with conn, conn.cursor() as cur:
        cur.execute(DDL)
        with cur.copy("COPY raw.osm_calles (osm_id, highway, nombre, etiquetas, nodos, geom) FROM STDIN") as copy:
            for i, e in ways.items():
                g = e["geometry"]
                if len(g) < 2 or any(p is None for p in g):
                    continue
                wkt = "SRID=4326;LINESTRING(" + ",".join(f"{p['lon']} {p['lat']}" for p in g) + ")"
                t = e.get("tags", {})
                nodos = "{" + ",".join(map(str, e["nodes"])) + "}"
                copy.write_row([i, t.get("highway"), t.get("name"), json.dumps(t, ensure_ascii=False), nodos, wkt])
        cur.execute("CREATE INDEX ON raw.osm_calles USING gist (geom)")
        cur.execute("""INSERT INTO raw.carga_externa_log (fuente, archivo, sha256, filas) VALUES (%s,%s,%s,%s)
            ON CONFLICT (fuente) DO UPDATE SET archivo=EXCLUDED.archivo, sha256=EXCLUDED.sha256,
            filas=EXCLUDED.filas, cargado_en=now()""",
            ("osm_calles_cdmx", "overpass 4x4 mosaicos", hashlib.sha256(json.dumps(sorted(ways)).encode()).hexdigest(), len(ways)))
    print("raw.osm_calles cargada")


if __name__ == "__main__":
    main()

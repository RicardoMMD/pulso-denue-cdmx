"""Carga a raw.osm_comercio las áreas comerciales de OpenStreetMap (centros comerciales, mercados, zonas de comercio).

Fuente: data/raw/externas/osm/comercio_areas.json (Overpass: shop=mall, amenity=marketplace, landuse=retail).
Solo ways cerrados (polígonos) y nodos (puntos). Las 21 relaciones se omiten: su geometría es compuesta.
Uso: uv run python cargar_osm_comercio.py
"""
import json, os
import psycopg
from cargar_raw import RAIZ, env

DDL = """
DROP TABLE IF EXISTS raw.osm_comercio;
CREATE TABLE raw.osm_comercio (
  osm_tipo text, osm_id bigint, categoria text, nombre text, etiquetas jsonb, geom geometry(geometry, 4326)
);
"""


def main():
    env()
    elementos = json.load(open(RAIZ / "data/raw/externas/osm/comercio_areas.json"))["elements"]
    conn = psycopg.connect(
        host=os.environ["PGHOST"], port=os.environ["PGPORT"], dbname=os.environ["PGDATABASE"],
        user=os.environ["PULSO_OWNER_USER"], password=os.environ["PULSO_OWNER_PASSWORD"])
    n = omitidos = 0
    with conn, conn.cursor() as cur:
        cur.execute(DDL)
        with cur.copy("COPY raw.osm_comercio FROM STDIN") as copy:
            for e in elementos:
                t = e.get("tags", {})
                cat = t.get("shop") or t.get("amenity") or t.get("landuse")
                if e["type"] == "node":
                    wkt = f"SRID=4326;POINT({e['lon']} {e['lat']})"
                elif e["type"] == "way" and len(e.get("geometry", [])) >= 4 and e["geometry"][0] == e["geometry"][-1]:
                    wkt = "SRID=4326;POLYGON((" + ",".join(f"{p['lon']} {p['lat']}" for p in e["geometry"]) + "))"
                else:
                    omitidos += 1
                    continue
                copy.write_row([e["type"], e["id"], cat, t.get("name"), json.dumps(t, ensure_ascii=False), wkt])
                n += 1
        cur.execute("CREATE INDEX ON raw.osm_comercio USING gist (geom)")
    print(f"raw.osm_comercio: {n} filas, {omitidos} omitidos (relaciones o geometrías abiertas)")


if __name__ == "__main__":
    main()

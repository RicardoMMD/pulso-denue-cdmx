"""Descarga (si falta) y carga a raw.osm_metro las líneas y estaciones del Metro (STC) de OpenStreetMap.

Consulta Overpass: relaciones route=subway del rectángulo de CDMX, sus nodos miembros (paradas) y los nodos
railway=station + station=subway. Se guarda en data/raw/externas/osm/metro.json.
Una fila por elemento: relaciones con sus miembros (jsonb) y nodos con su punto.
Uso: uv run python cargar_osm_metro.py [--descargar]
"""
import hashlib, json, os, subprocess, sys
import psycopg
from cargar_raw import RAIZ, env

ARCHIVO = RAIZ / "data" / "raw" / "externas" / "osm" / "metro.json"
BBOX = "19.04,-99.37,19.60,-98.94"
CONSULTA = (f'[out:json][timeout:180];(rel["route"="subway"]({BBOX});)->.r;.r out body;node(r.r)->.n;.n out body;'
            f'node["railway"="station"]["station"="subway"]({BBOX});out body;')

DDL = """
DROP TABLE IF EXISTS raw.osm_metro;
CREATE TABLE raw.osm_metro (
  osm_tipo text, osm_id bigint, etiquetas jsonb, miembros jsonb, geom geometry(point, 4326)
);
"""


def main():
    env()
    if "--descargar" in sys.argv or not ARCHIVO.exists():
        subprocess.run(["curl", "-s", "-m", "240", "-A", "pulso-denue/0.1", "--data-urlencode", f"data={CONSULTA}",
                        "https://overpass-api.de/api/interpreter", "-o", str(ARCHIVO)], check=True)
    elementos = json.loads(ARCHIVO.read_text())["elements"]
    vistos = set()
    conn = psycopg.connect(
        host=os.environ["PGHOST"], port=os.environ["PGPORT"], dbname=os.environ["PGDATABASE"],
        user=os.environ["PULSO_OWNER_USER"], password=os.environ["PULSO_OWNER_PASSWORD"])
    with conn, conn.cursor() as cur:
        cur.execute(DDL)
        with cur.copy("COPY raw.osm_metro FROM STDIN") as copy:
            for e in elementos:
                if (e["type"], e["id"]) in vistos:
                    continue
                vistos.add((e["type"], e["id"]))
                punto = f"SRID=4326;POINT({e['lon']} {e['lat']})" if e["type"] == "node" else None
                miembros = json.dumps(e.get("members"), ensure_ascii=False) if e["type"] == "relation" else None
                copy.write_row([e["type"], e["id"], json.dumps(e.get("tags", {}), ensure_ascii=False), miembros, punto])
        cur.execute("""INSERT INTO raw.carga_externa_log (fuente, archivo, sha256, filas) VALUES (%s,%s,%s,%s)
            ON CONFLICT (fuente) DO UPDATE SET archivo=EXCLUDED.archivo, sha256=EXCLUDED.sha256,
            filas=EXCLUDED.filas, cargado_en=now()""",
            ("osm_metro_cdmx", ARCHIVO.name, hashlib.sha256(ARCHIVO.read_bytes()).hexdigest(), len(vistos)))
    print(f"raw.osm_metro: {len(vistos)} elementos")


if __name__ == "__main__":
    main()

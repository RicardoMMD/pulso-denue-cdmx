"""Carga a raw el Marco Geoestadístico 2020 de INEGI para CDMX (capas de alcaldías, AGEB, localidades y manzanas).

Fuente: data/raw/externas/marco_geo_2020/conjunto_de_datos/09*.shp (descomprimido de 09_ciudaddemexico.zip).
Proyección de origen: Mexico ITRF2008 / LCC (EPSG 6372); se carga tal cual y se proyecta en dbt.
Lee cada capa con pyshp y construye la geometría en PostGIS (ST_GeomFromGeoJSON). Reemplaza las tablas raw.mg2020_*.
Uso: uv run python cargar_marco_geo.py
"""
import hashlib, json, os
import psycopg, shapefile
from cargar_raw import RAIZ, env

DIR = RAIZ / "data" / "raw" / "externas" / "marco_geo_2020"
SHP = DIR / "conjunto_de_datos"
ZIP = DIR / "09_ciudaddemexico.zip"

# sufijo de archivo -> tabla en raw
CAPAS = {
    "mun": "mg2020_municipio",      # áreas geoestadísticas municipales (alcaldías)
    "a": "mg2020_ageb_urbana",      # AGEB urbanas
    "ar": "mg2020_ageb_rural",      # AGEB rurales
    "l": "mg2020_localidad",        # polígonos de localidades urbanas y rurales amanzanadas
    "m": "mg2020_manzana",          # manzanas
}


def main():
    env()
    conn = psycopg.connect(
        host=os.environ["PGHOST"], port=os.environ["PGPORT"], dbname=os.environ["PGDATABASE"],
        user=os.environ["PULSO_OWNER_USER"], password=os.environ["PULSO_OWNER_PASSWORD"])
    with conn, conn.cursor() as cur:
        for sufijo, tabla in CAPAS.items():
            lector = shapefile.Reader(str(SHP / f"09{sufijo}"), encoding="latin-1")
            campos = [f[0].lower() for f in lector.fields[1:]]
            cur.execute(f"DROP TABLE IF EXISTS raw.{tabla}")
            cur.execute(f"CREATE TABLE raw.{tabla} ({', '.join(f'{c} text' for c in campos)}, geojson text)")
            with cur.copy(f"COPY raw.{tabla} ({', '.join(campos)}, geojson) FROM STDIN") as copy:
                for forma in lector.iterShapeRecords():
                    copy.write_row([None if v is None else str(v) for v in forma.record] +
                                   [json.dumps(forma.shape.__geo_interface__)])
            # geometría en la proyección de origen (EPSG 6372); multipolígono para todas las capas de área
            cur.execute(f"""ALTER TABLE raw.{tabla} ADD COLUMN geom geometry(multipolygon, 6372);
                UPDATE raw.{tabla} SET geom = ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(geojson), 6372));
                ALTER TABLE raw.{tabla} DROP COLUMN geojson;
                CREATE INDEX ON raw.{tabla} USING gist (geom);""")
            cur.execute(f"select count(*) from raw.{tabla}")
            print(f"raw.{tabla}: {cur.fetchone()[0]} filas")
        cur.execute("""CREATE TABLE IF NOT EXISTS raw.carga_externa_log (
            fuente text PRIMARY KEY, archivo text NOT NULL, sha256 text NOT NULL, filas integer NOT NULL,
            cargado_en timestamptz NOT NULL DEFAULT now())""")
        cur.execute("select count(*) from raw.mg2020_manzana")
        cur.execute("""INSERT INTO raw.carga_externa_log (fuente, archivo, sha256, filas) VALUES (%s,%s,%s,%s)
            ON CONFLICT (fuente) DO UPDATE SET archivo=EXCLUDED.archivo, sha256=EXCLUDED.sha256,
            filas=EXCLUDED.filas, cargado_en=now()""",
            ("marco_geoestadistico_2020_cdmx", ZIP.name, hashlib.sha256(ZIP.read_bytes()).hexdigest(), cur.fetchone()[0]))


if __name__ == "__main__":
    main()

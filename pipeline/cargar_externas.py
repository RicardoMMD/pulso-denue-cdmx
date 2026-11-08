"""Carga las fuentes geográficas externas a raw (GeoJSON de datos abiertos CDMX).

Uso: uv run python cargar_externas.py
Reemplaza el contenido de raw.colonias_cdmx, raw.mercados_publicos, raw.tianguis y raw.mercados_sobre_ruedas.
"""
import json, os, pathlib
import psycopg
from cargar_raw import RAIZ, env

EXT = RAIZ / "data" / "raw" / "externas"

DDL = """
CREATE TABLE IF NOT EXISTS raw.colonias_cdmx (
  cve_ent text, entidad text, cve_alc text, alcaldia text, cve_col text, colonia text, clasif text,
  geom geometry(geometry, 4326)
);
CREATE TABLE IF NOT EXISTS raw.mercados_publicos (
  numero text, alcaldia text, mercado text, num_oficial text, num_locales text, direccion text,
  colonia text, tipo text, superficie_m2 text, inauguracion text, vocacion text, forma text, niveles text,
  tamano text, protegido text, longitud text, latitud text, geom geometry(point, 4326)
);
CREATE TABLE IF NOT EXISTS raw.tianguis (
  alcaldia text, colonia text, giro text, dia text, horario text, ubicacion text, num_oferentes text,
  geom geometry(point, 4326)
);
CREATE TABLE IF NOT EXISTS raw.mercados_sobre_ruedas (
  ruta text, dia text, num_oferentes text, direccion text, alcaldia text, colonia text, punto text,
  geom geometry(point, 4326)
);
"""


def main():
    env()
    conn = psycopg.connect(
        host=os.environ["PGHOST"], port=os.environ["PGPORT"], dbname=os.environ["PGDATABASE"],
        user=os.environ["PULSO_OWNER_USER"], password=os.environ["PULSO_OWNER_PASSWORD"])
    with conn, conn.cursor() as cur:
        cur.execute(DDL)
        cur.execute("TRUNCATE raw.colonias_cdmx, raw.mercados_publicos, raw.tianguis, raw.mercados_sobre_ruedas")
        col = json.loads((EXT / "colonias.geojson").read_text())["features"]
        for f in col:
            p = f["properties"]
            cur.execute(
                "INSERT INTO raw.colonias_cdmx VALUES (%s,%s,%s,%s,%s,%s,%s, ST_Force2D(ST_SetSRID(ST_GeomFromGeoJSON(%s),4326)))",
                (p["cve_ent"], p["entidad"], p["cve_alc"], p["alc"], p["cve_col"], p["colonia"], p["clasif"],
                 json.dumps(f["geometry"])))
        mer = json.loads((EXT / "mercados.geojson").read_text())["features"]
        for f in mer:
            p = f["properties"]
            g = json.dumps(f["geometry"])
            cur.execute(
                "INSERT INTO raw.mercados_publicos VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, ST_Force2D(ST_SetSRID(ST_GeomFromGeoJSON(%s),4326)))",
                (p.get("N°"), p.get("DELEGACION"), p.get("MERCADO"), p.get("NUM_OFIC"), p.get("NUM_LOCALE"),
                 p.get("DIRECCION"), p.get("COLONIA"), p.get("TIPO"), p.get("SUPERF_M2"), p.get("INAUGURACI"),
                 p.get("VOCACIÓN"), p.get("FORMA"), p.get("NIVELES"), p.get("TAMAÑO1"), p.get("PROTEGIDO"),
                 p.get("COORGEOG_X"), p.get("COORGEOG_Y"), g))
        tia = json.loads((EXT / "tianguis.geojson").read_text())["features"]
        for f in tia:
            p = f["properties"]
            cur.execute(
                "INSERT INTO raw.tianguis VALUES (%s,%s,%s,%s,%s,%s,%s, ST_Force2D(ST_SetSRID(ST_GeomFromGeoJSON(%s),4326)))",
                (p.get("ALCALDÍA"), p.get("NOMBRE_COL"), p.get("GIRO"), p.get("DÍA"), p.get("HORARIO"),
                 p.get("UBIC_"), p.get("NUM_OFER_1"), json.dumps(f["geometry"])))
        msr = json.loads((EXT / "mercados_sobre_ruedas.geojson").read_text())["features"]
        for f in msr:
            p = f["properties"]
            cur.execute(
                "INSERT INTO raw.mercados_sobre_ruedas VALUES (%s,%s,%s,%s,%s,%s,%s, ST_Force2D(ST_SetSRID(ST_GeomFromGeoJSON(%s),4326)))",
                (p.get("Ruta"), p.get("Día_Oper"), p.get("Num_Oferen"), p.get("Dirección"), p.get("Alcaldía"),
                 p.get("Colonia"), p.get("PUNTO"), json.dumps(f["geometry"])))
    print(f"{len(col)} colonias, {len(mer)} mercados, {len(tia)} tianguis, {len(msr)} mercados sobre ruedas cargados")


if __name__ == "__main__":
    main()

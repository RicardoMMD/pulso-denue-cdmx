"""Carga los Censos Económicos 2024 (CDMX) a raw, tal como vienen: todo texto.

Uso: uv run python cargar_ce.py
Lee data/raw/externas/ce2024_cdmx/ (datos abiertos de INEGI). Reemplaza el contenido de las tablas raw.ce2024_*.
"""
import csv, hashlib, os, pathlib
import psycopg
from cargar_raw import RAIZ, env

DIR = RAIZ / "data" / "raw" / "externas" / "ce2024_cdmx"
ZIP = DIR / "ce_cdmx_2024_csv.zip"


def leer(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        lector = csv.reader(f)
        cab = [c.strip().lower() for c in next(lector)]
        return cab, [[(v.strip() or None) for v in fila] for fila in lector]


def cargar(cur, tabla, cab, filas):
    cur.execute(f"DROP TABLE IF EXISTS raw.{tabla}")
    cur.execute(f"CREATE TABLE raw.{tabla} ({', '.join(f'{c} text' for c in cab)})")
    with cur.copy(f"COPY raw.{tabla} ({', '.join(cab)}) FROM STDIN") as copy:
        for fila in filas:
            copy.write_row(fila)
    print(f"raw.{tabla}: {len(filas)} filas")


def main():
    env()
    conn = psycopg.connect(
        host=os.environ["PGHOST"], port=os.environ["PGPORT"], dbname=os.environ["PGDATABASE"],
        user=os.environ["PULSO_OWNER_USER"], password=os.environ["PULSO_OWNER_PASSWORD"])
    with conn, conn.cursor() as cur:
        cab, filas = leer(DIR / "conjunto_de_datos" / "tr_ce_cdmx_2024.csv")
        cargar(cur, "ce2024_cdmx", cab, filas)
        total = len(filas)
        cab, filas = leer(DIR / "diccionario_de_datos" / "diccionario_de_datos_ce2024.csv")
        cargar(cur, "ce2024_diccionario", cab, filas)
        cab, filas = leer(DIR / "catalogos" / "tc_codigo_actividad.csv")
        cab = [c for c in cab if c]
        filas = [f[:len(cab)] for f in filas]
        cargar(cur, "ce2024_catalogo_actividad", cab, filas)
        cur.execute("""CREATE TABLE IF NOT EXISTS raw.carga_externa_log (
            fuente text PRIMARY KEY, archivo text NOT NULL, sha256 text NOT NULL, filas integer NOT NULL,
            cargado_en timestamptz NOT NULL DEFAULT now())""")
        cur.execute("""INSERT INTO raw.carga_externa_log (fuente, archivo, sha256, filas) VALUES (%s,%s,%s,%s)
            ON CONFLICT (fuente) DO UPDATE SET archivo=EXCLUDED.archivo, sha256=EXCLUDED.sha256,
            filas=EXCLUDED.filas, cargado_en=now()""",
            ("censos_economicos_2024_cdmx", ZIP.name, hashlib.sha256(ZIP.read_bytes()).hexdigest(), total))


if __name__ == "__main__":
    main()

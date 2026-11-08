"""Carga un CSV del DENUE (CDMX) a raw.denue, tal como viene: todo texto, sin limpiar.

Uso: uv run python cargar_raw.py <edicion> <csv> [<publicacion>]
  edicion      AAAA-MM, por ejemplo 2026-05
  publicacion  fecha de publicación según los metadatos (AAAA-MM-DD)

Conexión por variables PG* y PULSO_OWNER_* del .env (túnel a localhost:55432).
Es idempotente: reemplaza la edición si ya estaba cargada.
"""
import csv, hashlib, io, os, pathlib, sys
import psycopg

RAIZ = pathlib.Path(__file__).resolve().parents[1]

COLUMNAS = [
    "id", "clee", "nom_estab", "raz_social", "codigo_act", "nombre_act", "per_ocu",
    "tipo_vial", "nom_vial", "tipo_v_e_1", "nom_v_e_1", "tipo_v_e_2", "nom_v_e_2",
    "tipo_v_e_3", "nom_v_e_3", "numero_ext", "letra_ext", "edificio", "edificio_e",
    "numero_int", "letra_int", "tipo_asent", "nomb_asent", "tipocencom", "nom_cencom",
    "num_local", "cod_postal", "cve_ent", "entidad", "cve_mun", "municipio", "cve_loc",
    "localidad", "ageb", "manzana", "telefono", "correoelec", "www", "tipounieco",
    "latitud", "longitud", "fecha_alta",
]

DDL = f"""
CREATE TABLE IF NOT EXISTS raw.denue (
  edicion text NOT NULL,
  {', '.join(f'{c} text' for c in COLUMNAS)}
);
CREATE INDEX IF NOT EXISTS denue_edicion_idx ON raw.denue (edicion);
CREATE TABLE IF NOT EXISTS raw.carga_log (
  edicion text PRIMARY KEY,
  publicacion date,
  archivo text NOT NULL,
  sha256 text NOT NULL,
  filas integer NOT NULL,
  cargado_en timestamptz NOT NULL DEFAULT now()
);
"""


def env():
    for linea in (RAIZ / ".env").read_text().splitlines():
        if "=" in linea and not linea.startswith("#"):
            k, v = linea.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main(edicion, ruta, publicacion=None):
    env()
    ruta = pathlib.Path(ruta)
    sha = hashlib.sha256(ruta.read_bytes()).hexdigest()
    conn = psycopg.connect(
        host=os.environ["PGHOST"], port=os.environ["PGPORT"], dbname=os.environ["PGDATABASE"],
        user=os.environ["PULSO_OWNER_USER"], password=os.environ["PULSO_OWNER_PASSWORD"],
    )
    with conn, conn.cursor() as cur:
        cur.execute(DDL)
        cur.execute("DELETE FROM raw.denue WHERE edicion = %s", (edicion,))
        with open(ruta, encoding="latin-1", newline="") as f:
            lector = csv.reader(f)
            cab = [c.lower() for c in next(lector)]
            assert cab == COLUMNAS, f"columnas distintas: {set(cab) ^ set(COLUMNAS)}"
            cols = ", ".join(["edicion"] + COLUMNAS)
            filas = 0
            with cur.copy(f"COPY raw.denue ({cols}) FROM STDIN") as copy:
                for fila in lector:
                    copy.write_row([edicion] + [v if v != "" else None for v in fila])
                    filas += 1
        cur.execute(
            """INSERT INTO raw.carga_log (edicion, publicacion, archivo, sha256, filas)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (edicion) DO UPDATE SET publicacion = EXCLUDED.publicacion,
                 archivo = EXCLUDED.archivo, sha256 = EXCLUDED.sha256, filas = EXCLUDED.filas,
                 cargado_en = now()""",
            (edicion, publicacion, ruta.name, sha, filas),
        )
    print(f"{edicion}: {filas} filas cargadas desde {ruta.name}")


if __name__ == "__main__":
    main(*sys.argv[1:4])

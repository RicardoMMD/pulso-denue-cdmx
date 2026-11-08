"""Carga a raw el Censo de Población y Vivienda 2020 de INEGI para CDMX, tal como viene: todo texto.

- raw.censo2020_ageb_mza: resultados por AGEB y manzana urbana (una fila por total de entidad, alcaldía,
  localidad, AGEB o manzana; los totales llevan claves 0000 / 000).
- raw.censo2020_iter: principales resultados por localidad (ITER), incluye localidades rurales.
Los valores '*' son confidenciales y 'N/D' no disponibles; se tipan en dbt.
Fuente: data/raw/externas/censo2020/ (descomprimidos). Uso: uv run python cargar_censo2020.py
"""
import hashlib, os
import psycopg
from cargar_raw import RAIZ, env
from cargar_ce import leer, cargar

DIR = RAIZ / "data" / "raw" / "externas" / "censo2020"


def main():
    env()
    conn = psycopg.connect(
        host=os.environ["PGHOST"], port=os.environ["PGPORT"], dbname=os.environ["PGDATABASE"],
        user=os.environ["PULSO_OWNER_USER"], password=os.environ["PULSO_OWNER_PASSWORD"])
    with conn, conn.cursor() as cur:
        cab, filas = leer(DIR / "ageb_mza_urbana_09_cpv2020" / "conjunto_de_datos" / "conjunto_de_datos_ageb_urbana_09_cpv2020.csv")
        cargar(cur, "censo2020_ageb_mza", cab, filas)
        n = len(filas)
        cab, filas = leer(DIR / "iter_09_cpv2020" / "conjunto_de_datos" / "conjunto_de_datos_iter_09CSV20.csv")
        cargar(cur, "censo2020_iter", cab, filas)
        cur.execute("""CREATE TABLE IF NOT EXISTS raw.carga_externa_log (
            fuente text PRIMARY KEY, archivo text NOT NULL, sha256 text NOT NULL, filas integer NOT NULL,
            cargado_en timestamptz NOT NULL DEFAULT now())""")
        for fuente, archivo, filas_n in [("censo2020_ageb_mza_cdmx", "ageb_mza_urbana_09_cpv2020_csv.zip", n),
                                         ("censo2020_iter_cdmx", "iter_09_cpv2020_csv.zip", len(filas))]:
            cur.execute("""INSERT INTO raw.carga_externa_log (fuente, archivo, sha256, filas) VALUES (%s,%s,%s,%s)
                ON CONFLICT (fuente) DO UPDATE SET archivo=EXCLUDED.archivo, sha256=EXCLUDED.sha256,
                filas=EXCLUDED.filas, cargado_en=now()""",
                (fuente, archivo, hashlib.sha256((DIR / archivo).read_bytes()).hexdigest(), filas_n))


if __name__ == "__main__":
    main()

"""Exporta el catálogo de referencias de una edición desde `semantic` a `referencias/<edicion>.json` (R12).

Lee con el rol `pulso_analista` (solo lectura, la misma superficie que el Analista): si algo no está en `semantic`,
el contrato no lo puede referenciar, y eso es intencional. Requiere el túnel y el .env:

    make referencias            # o: cd backend && uv run --group base python -m contracts.exportar_referencias 2026-05

`semantic.lugar` no tiene edición (es el catálogo vigente), así que solo se exporta la edición vigente.
El archivo no lleva coordenadas ni geometrías: el contrato no las necesita.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

DESTINO = Path(__file__).resolve().parent / "referencias"
TIPOS_LUGAR = ("ciudad", "alcaldia", "colonia", "estacion_metro", "conglomerado", "calle")


def conectar():
    import psycopg  # solo el exportador lo necesita (grupo `base`)

    conn = psycopg.connect(
        host=os.environ["PGHOST"], port=os.environ["PGPORT"], dbname=os.environ["PGDATABASE"],
        user=os.environ["PULSO_ANALISTA_USER"], password=os.environ["PULSO_ANALISTA_PASSWORD"])
    conn.read_only = True
    return conn


def codigos_scian(clases: list[str]) -> list[str]:
    """Sector (2 dígitos) a clase (6): todos los prefijos de las clases de la versión vigente."""
    return sorted({c[:n] for c in clases for n in range(2, 7) if len(c) >= n})


def exportar(conn, edicion: str) -> dict:
    fila = conn.execute(
        "select edicion, fecha_corte, version_scian, es_vigente from semantic.edicion where edicion = %s", (edicion,)
    ).fetchone()
    if fila is None:
        raise SystemExit(f"La edición {edicion} no existe en semantic.edicion.")
    _, fecha_corte, version_scian, es_vigente = fila
    if not es_vigente:
        raise SystemExit(f"{edicion} no es la edición vigente y semantic.lugar solo describe la vigente.")

    lugares: dict[str, dict[str, str]] = {t: {} for t in TIPOS_LUGAR}
    for tipo, clave, nombre in conn.execute("select tipo, clave, nombre from semantic.lugar order by tipo, clave"):
        lugares[tipo][clave] = nombre

    lineas: dict[str, dict] = {}
    for cve, nombre, estacion_norm in conn.execute(
            "select cve_linea, linea, estacion_norm from semantic.metro_recorrido order by cve_linea, orden"):
        lineas.setdefault(cve, {"nombre": nombre, "estaciones": []})["estaciones"].append(estacion_norm)

    clases = [r[0] for r in conn.execute(
        "select clase_scian from semantic.actividad where version_scian = %s", (version_scian,))]
    tipos = [r[0] for r in conn.execute(
        "select distinct tipo from semantic.conglomerado where edicion = %s order by 1", (edicion,))]

    return {
        "edicion": edicion,
        "fecha_corte": fecha_corte.isoformat(),
        "version_scian": version_scian,
        "lugares": lugares,
        "lineas": lineas,
        "scian": codigos_scian(clases),
        "tipos_conglomerado": tipos,
    }


def escribir(datos: dict) -> Path:
    DESTINO.mkdir(exist_ok=True)
    ruta = DESTINO / f"{datos['edicion']}.json"
    # indent=0: una entrada por línea, sin sangría (diffs legibles y archivo chico).
    ruta.write_text(json.dumps(datos, indent=0, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return ruta


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python -m contracts.exportar_referencias <edicion>   (por ejemplo 2026-05)", file=sys.stderr)
        return 2
    with conectar() as conn:
        datos = exportar(conn, sys.argv[1])
    ruta = escribir(datos)
    n = {t: len(v) for t, v in datos["lugares"].items()}
    print(f"escrito {ruta} ({ruta.stat().st_size / 1e6:.2f} MB): lugares {n}, líneas {len(datos['lineas'])}, "
          f"códigos SCIAN {len(datos['scian'])}, tipos de conglomerado {len(datos['tipos_conglomerado'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

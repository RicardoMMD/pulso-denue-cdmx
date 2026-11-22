"""Exporta el catálogo de clases SCIAN a datos/clases.json. Se corre una vez, con túnel.

Solo lee, con el rol del Analista (`semantic`, solo lectura). Trae además las palabras más frecuentes
de los nombres comerciales de cada clase, para no volver a necesitar la base al afinar.

Uso: make catalogo
"""
import json
import os
import re
from collections import Counter, defaultdict
from datetime import date

import psycopg

from comun import DATOS, normalizar

VERSION = "SCIAN 2023"
PALABRAS_POR_CLASE = 12
# Una palabra cuenta para una clase si aparece al menos en 3 establecimientos y en 2 % de la clase,
# y si es al menos 3 veces más común ahí que en toda la ciudad (deja fuera "MEXICO", "GRUPO", "SERVICIOS").
MIN_ESTABLECIMIENTOS, MIN_PARTE, MIN_VECES = 3, 0.02, 3.0
VACIAS = set("DEL LAS LOS POR CON SIN PARA UNA UNO QUE SAN SANTA THE AND".split())

COLUMNAS = ["clase_scian", "nombre_clase", "cve_subrama", "nombre_subrama", "cve_rama", "nombre_rama",
            "cve_subsector", "nombre_subsector", "nombre_subsector_corto", "cve_sector", "nombre_sector",
            "cve_macrosector", "nombre_macrosector", "establecimientos_vigente"]


def main():
    conn = psycopg.connect(host=os.environ["PGHOST"], port=os.environ["PGPORT"], dbname=os.environ["PGDATABASE"],
                           user=os.environ["PULSO_ANALISTA_USER"], password=os.environ["PULSO_ANALISTA_PASSWORD"])
    conn.read_only = True
    cur = conn.cursor()

    cur.execute(f"select {', '.join(COLUMNAS)} from semantic.actividad where version_scian = %s order by clase_scian",
                (VERSION,))
    clases = [dict(zip(COLUMNAS, fila)) for fila in cur.fetchall()]

    cur.execute("select distinct edicion, fecha_corte from semantic.establecimiento where edicion_vigente")
    edicion, fecha_corte = cur.fetchone()

    # Por sector, para que ninguna consulta se acerque al límite de 8 s del rol.
    por_clase, ciudad, totales = defaultdict(Counter), Counter(), Counter()
    for sector in sorted({c["cve_sector"] for c in clases}):
        cur.execute("select clase_scian_2023, nombre from semantic.establecimiento "
                    "where edicion_vigente and cve_sector = %s", (sector,))
        for clase, nombre in cur:
            totales[clase] += 1
            palabras = {p for p in re.findall(r"[A-ZÑ]{3,}", normalizar(nombre or "")) if p not in VACIAS}
            por_clase[clase].update(palabras)
            ciudad.update(palabras)
    total_ciudad = sum(totales.values())

    for c in clases:
        n = totales.get(c["clase_scian"], 0)
        elegidas = []
        for palabra, veces in por_clase[c["clase_scian"]].most_common():
            if veces < MIN_ESTABLECIMIENTOS or veces / n < MIN_PARTE:
                break
            if (veces / n) / (ciudad[palabra] / total_ciudad) >= MIN_VECES:
                elegidas.append({"palabra": palabra, "establecimientos": veces, "parte": round(veces / n, 3)})
            if len(elegidas) == PALABRAS_POR_CLASE:
                break
        c["palabras_frecuentes"] = elegidas

    salida = {
        "fuente": "semantic.actividad y semantic.establecimiento (DENUE, INEGI)",
        "version_scian": VERSION,
        "edicion": edicion,
        "fecha_corte": fecha_corte.isoformat(),
        "exportado": date.today().isoformat(),
        "clases": clases,
    }
    DATOS.mkdir(exist_ok=True)
    ruta = DATOS / "clases.json"
    ruta.write_text(json.dumps(salida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    con_palabras = sum(1 for c in clases if c["palabras_frecuentes"])
    print(f"escrito {ruta}: {len(clases)} clases, {con_palabras} con palabras frecuentes, "
          f"{total_ciudad} establecimientos leídos (edición {edicion})")


if __name__ == "__main__":
    main()

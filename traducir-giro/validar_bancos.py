"""Revisa la forma de los bancos y que sus clases existan en el catálogo. Sin base, sin modelos, sin dependencias.

Lo corre `make check` del proyecto principal. Si todavía no hay bancos, solo revisa el catálogo.
No abre el contenido del banco ciego en pantalla: solo dice si está bien formado.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
TIPOS = {"calle", "descripcion", "error_dedo", "no_es_giro"}
MINIMO = {"ajuste": 60, "ciego": 50}


def main():
    catalogo = json.loads((RAIZ / "datos" / "clases.json").read_text(encoding="utf-8"))
    validas = {c["clase_scian"] for c in catalogo["clases"]}
    errores, vistos = [], {}
    if len(validas) != len(catalogo["clases"]):
        errores.append("catálogo: hay clases repetidas")

    for nombre in ("ajuste", "ciego"):
        ruta = RAIZ / "bancos" / f"{nombre}.json"
        if not ruta.exists():
            continue
        casos = json.loads(ruta.read_text(encoding="utf-8"))["casos"]
        if len(casos) < MINIMO[nombre]:
            errores.append(f"{nombre}: {len(casos)} casos, faltan para llegar a {MINIMO[nombre]}")
        faltan = TIPOS - {c.get("tipo") for c in casos}
        if faltan:
            errores.append(f"{nombre}: no hay casos de tipo {', '.join(sorted(faltan))}")
        for i, c in enumerate(casos, 1):
            donde = f"{nombre} caso {i}"
            termino, tipo, clases = c.get("termino"), c.get("tipo"), c.get("clases")
            if not isinstance(termino, str) or not termino.strip():
                errores.append(f"{donde}: falta el término")
                continue
            if tipo not in TIPOS:
                errores.append(f"{donde}: tipo desconocido")
            if not isinstance(clases, list):
                errores.append(f"{donde}: 'clases' debe ser una lista")
                continue
            if tipo == "no_es_giro" and clases:
                errores.append(f"{donde}: un caso que no es giro no lleva clases")
            if tipo != "no_es_giro" and not clases:
                errores.append(f"{donde}: falta al menos una clase aceptable")
            if any(x not in validas for x in clases):
                errores.append(f"{donde}: clase que no está en el catálogo")
            llave = termino.strip().lower()
            if llave in vistos:
                errores.append(f"{donde}: término repetido (ya está en {vistos[llave]})")
            vistos[llave] = donde

    ruta = RAIZ / "glosario.json"
    if ruta.exists():
        claves = set()
        for i, e in enumerate(json.loads(ruta.read_text(encoding="utf-8"))["entradas"], 1):
            if any(x not in validas for x in e["clases"]):
                errores.append(f"glosario entrada {i}: clase que no está en el catálogo")
            if not e["clases"] and not e.get("nota"):
                errores.append(f"glosario entrada {i}: sin clases y sin nota")
            for nombre in [e["termino"], *e.get("variantes", [])]:
                if nombre.strip().lower() in claves:
                    errores.append(f"glosario entrada {i}: término o variante repetida")
                claves.add(nombre.strip().lower())

    if errores:
        print("\n".join(errores))
        sys.exit(1)


if __name__ == "__main__":
    main()

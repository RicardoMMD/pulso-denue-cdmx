"""Convierte cada clase del catálogo en un vector, por modelo, y lo guarda en vectores/ (no versionado).

Uso:
  uv run python vectorizar.py                      todos los modelos descargados, texto simple
  uv run python vectorizar.py qwen3 --variante palabras
"""
import argparse
import hashlib
import json
import time
from datetime import datetime

import numpy as np

from comun import MODELOS, VARIANTES, VECTORES, cargar_modelo, codificar, leer_catalogo, ruta_modelo


def rutas(nombre, variante):
    base = VECTORES / nombre
    return base / f"{variante}.npz", base / f"{variante}.json"


def vectorizar(nombre, variante):
    catalogo = leer_catalogo()
    textos = [VARIANTES[variante](c) for c in catalogo["clases"]]
    modelo = cargar_modelo(nombre)
    inicio = time.perf_counter()
    vectores = codificar(modelo, nombre, textos, "documento").astype(np.float32)
    segundos = time.perf_counter() - inicio

    npz, meta = rutas(nombre, variante)
    npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez(npz, codigos=np.array([c["clase_scian"] for c in catalogo["clases"]]), vectores=vectores)
    meta.write_text(json.dumps({
        "modelo": nombre, "repo": MODELOS[nombre]["repo"], "revision": MODELOS[nombre]["revision"],
        "variante": variante, "instruccion_documento": MODELOS[nombre]["documento"],
        "clases": len(textos), "dimensiones": int(vectores.shape[1]),
        "huella_textos": hashlib.sha256("\n".join(textos).encode()).hexdigest()[:16],
        "edicion_catalogo": catalogo["edicion"], "segundos": round(segundos, 1),
        "creado": datetime.now().isoformat(timespec="seconds"), "ejemplo_texto": textos[0],
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{nombre}/{variante}: {vectores.shape[0]} clases × {vectores.shape[1]} dimensiones en {segundos:.1f} s")


def leer_vectores(nombre, variante):
    npz, _ = rutas(nombre, variante)
    if not npz.exists():
        raise SystemExit(f"Faltan los vectores de {nombre}/{variante}. Corre: uv run python vectorizar.py {nombre} "
                         f"--variante {variante}")
    datos = np.load(npz)
    return datos["codigos"], datos["vectores"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("modelo", nargs="?", choices=list(MODELOS))
    p.add_argument("--variante", default="simple", choices=list(VARIANTES))
    a = p.parse_args()
    nombres = [a.modelo] if a.modelo else [n for n in MODELOS if (ruta_modelo(n) / "modules.json").exists()]
    if not nombres:
        raise SystemExit("No hay modelos descargados. Mira: uv run python descargar.py")
    for nombre in nombres:
        vectorizar(nombre, a.variante)


if __name__ == "__main__":
    main()

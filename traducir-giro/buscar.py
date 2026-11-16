"""Término → clases SCIAN más cercanas.

Uso: uv run python buscar.py qwen3 "donde arreglan celulares" [--variante simple] [-k 10]
"""
import argparse

import numpy as np

from comun import MODELOS, VARIANTES, cargar_modelo, codificar, leer_catalogo
from vectorizar import leer_vectores


def mas_cercanas(vector_consulta, codigos, vectores, k=10):
    """Lista de (clase, parecido) de mayor a menor. Los vectores vienen normalizados: el producto es el coseno."""
    parecidos = vectores @ vector_consulta
    orden = np.argsort(-parecidos)[:k]
    return [(str(codigos[i]), float(parecidos[i])) for i in orden]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("modelo", choices=list(MODELOS))
    p.add_argument("termino")
    p.add_argument("--variante", default="simple", choices=list(VARIANTES))
    p.add_argument("-k", type=int, default=10)
    a = p.parse_args()

    nombres = {c["clase_scian"]: c for c in leer_catalogo()["clases"]}
    codigos, vectores = leer_vectores(a.modelo, a.variante)
    modelo = cargar_modelo(a.modelo)
    consulta = codificar(modelo, a.modelo, [a.termino], "consulta")[0]
    for clase, parecido in mas_cercanas(consulta, codigos, vectores, a.k):
        c = nombres[clase]
        print(f"{parecido:.3f}  {clase}  {c['nombre_clase']}  ({c['establecimientos_vigente']} establecimientos)")


if __name__ == "__main__":
    main()

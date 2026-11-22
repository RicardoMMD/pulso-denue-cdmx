"""Corre un banco contra los modelos y escribe resultados/.

Uso:
  uv run python evaluar.py ajuste                       todos los modelos con vectores, texto simple
  uv run python evaluar.py ajuste --variante palabras
  uv run python evaluar.py ajuste --modelo qwen3        un solo modelo (así lo lanza la corrida completa)
  uv run python evaluar.py ciego --confirmo-ciego       UNA sola vez, al final

Cada modelo se mide en su propio proceso, para que la memoria reportada sea solo la suya.
El umbral de parecido se fija en el banco de ajuste y el ciego lo lee: no se recalcula.
Termina con error si se corre el banco ciego y ningún modelo cumple C1–C4.
"""
import argparse
import json
import resource
import statistics
import subprocess
import sys
import time
from datetime import datetime

from comun import MODELOS, NOMBRE_TIPO, RESULTADOS, TIPOS, VARIANTES, leer_banco, leer_catalogo
from vectorizar import rutas

# Criterios del README. Se confirman antes de correr el banco ciego y no se mueven después.
C1_PRIMEROS_5 = 0.85
C2_POR_TIPO = 0.70
C3_RECHAZO, C3_PERDIDA_MAX = 0.80, 0.05
C4_MEMORIA_GB, C4_MS = 2.0, 200

# Modelos que no entran al banco ciego (ver main).
EXCLUIDOS_CIEGO = {"qwen3"}


def ruta_resultado(banco, variante, modelo):
    return RESULTADOS / banco / f"{modelo}.{variante}.json"


def ruta_umbrales():
    return RESULTADOS / "umbrales.json"


def fijar_umbral(parecidos_giro):
    """El umbral más alto que pierde como máximo 5 % de los giros reales. Se rechaza lo que queda por debajo."""
    ordenados = sorted(parecidos_giro)
    return ordenados[int(C3_PERDIDA_MAX * len(ordenados))]


def parte(aciertos, total):
    return round(aciertos / total, 4) if total else None


def medir(banco, variante, nombre, hilos):
    """Un modelo sobre un banco. Corre en su propio proceso."""
    import psutil
    import torch

    from buscar import mas_cercanas
    from comun import cargar_modelo, codificar
    from vectorizar import leer_vectores

    if hilos:
        torch.set_num_threads(hilos)
    catalogo = {c["clase_scian"]: c for c in leer_catalogo()["clases"]}
    casos = leer_banco(banco)["casos"]
    codigos, vectores = leer_vectores(nombre, variante)
    modelo = cargar_modelo(nombre)
    codificar(modelo, nombre, ["calentamiento"], "consulta")

    filas, tiempos = [], []
    for caso in casos:
        inicio = time.perf_counter()
        consulta = codificar(modelo, nombre, [caso["termino"]], "consulta")[0]
        cercanas = mas_cercanas(consulta, codigos, vectores, 10)
        tiempos.append((time.perf_counter() - inicio) * 1000)
        posicion = next((i + 1 for i, (clase, _) in enumerate(cercanas) if clase in caso["clases"]), None)
        filas.append({
            "termino": caso["termino"], "tipo": caso["tipo"], "clases": caso["clases"],
            "posicion": posicion, "parecido": round(cercanas[0][1], 4),
            "candidatos": [{"clase": clase, "nombre": catalogo[clase]["nombre_clase"], "parecido": round(p, 4),
                            "acierta": clase in caso["clases"]} for clase, p in cercanas],
        })

    giros = [f for f in filas if f["tipo"] != "no_es_giro"]
    no_giros = [f for f in filas if f["tipo"] == "no_es_giro"]

    clave = f"{nombre}.{variante}"
    umbrales = json.loads(ruta_umbrales().read_text()) if ruta_umbrales().exists() else {}
    if banco == "ajuste":
        umbrales[clave] = round(fijar_umbral([f["parecido"] for f in giros]), 4)
        ruta_umbrales().parent.mkdir(exist_ok=True)
        ruta_umbrales().write_text(json.dumps(umbrales, indent=1, sort_keys=True) + "\n")
    elif clave not in umbrales:
        raise SystemExit(f"No hay umbral para {clave}: corre antes el banco de ajuste con esta variante.")
    umbral = umbrales[clave]
    for f in filas:
        f["rechazado"] = f["parecido"] < umbral

    def aciertos(grupo, k):
        return parte(sum(1 for f in grupo if f["posicion"] and f["posicion"] <= k), len(grupo))

    metricas = {
        "casos": len(filas), "giros": len(giros), "no_giros": len(no_giros),
        "primero": aciertos(giros, 1), "primeros_5": aciertos(giros, 5), "primeros_10": aciertos(giros, 10),
        "por_tipo": {t: {"casos": len(g), "primero": aciertos(g, 1), "primeros_5": aciertos(g, 5),
                         "primeros_10": aciertos(g, 10)}
                     for t in TIPOS if t != "no_es_giro" for g in [[f for f in giros if f["tipo"] == t]]},
        "umbral": umbral,
        "rechazo_no_giro": parte(sum(f["rechazado"] for f in no_giros), len(no_giros)),
        "giros_perdidos": parte(sum(f["rechazado"] for f in giros), len(giros)),
        "ms_mediana": round(statistics.median(tiempos), 1),
        "ms_p95": round(sorted(tiempos)[int(0.95 * (len(tiempos) - 1))], 1),
        "memoria_gb": round(psutil.Process().memory_info().rss / 1e9, 2),
        "memoria_pico_gb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024 / 1e9, 2),
        "hilos": torch.get_num_threads(),
    }
    meta_vectores = json.loads(rutas(nombre, variante)[1].read_text())
    salida = {
        "banco": banco, "modelo": nombre, "repo": MODELOS[nombre]["repo"], "revision": MODELOS[nombre]["revision"],
        "variante": variante, "instruccion_consulta": MODELOS[nombre]["consulta"],
        "instruccion_documento": MODELOS[nombre]["documento"], "huella_textos": meta_vectores["huella_textos"],
        "corrido": datetime.now().isoformat(timespec="seconds"), "metricas": metricas, "casos": filas,
    }
    ruta = ruta_resultado(banco, variante, nombre)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(salida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{nombre}/{variante} en {banco}: primeros 5 = {metricas['primeros_5']}, "
          f"rechazo = {metricas['rechazo_no_giro']}, {metricas['ms_mediana']} ms, {metricas['memoria_pico_gb']} GB")


def cumple(m):
    """Los criterios C1–C4 sobre las métricas de un modelo."""
    return {
        "C1": m["primeros_5"] is not None and m["primeros_5"] >= C1_PRIMEROS_5,
        "C2": all(t["primeros_5"] is not None and t["primeros_5"] >= C2_POR_TIPO for t in m["por_tipo"].values()),
        "C3": (m["rechazo_no_giro"] or 0) >= C3_RECHAZO and (m["giros_perdidos"] or 0) <= C3_PERDIDA_MAX,
        "C4": m["memoria_pico_gb"] < C4_MEMORIA_GB and m["ms_mediana"] < C4_MS,
    }


def pct(x):
    return "—" if x is None else f"{100 * x:.0f} %"


def comparar(banco, variante, nombres):
    """Tabla comparativa en resultados/<banco>-<variante>.md. Devuelve cuántos modelos cumplen C1–C4."""
    corridas = {n: json.loads(ruta_resultado(banco, variante, n).read_text()) for n in nombres}
    primera = next(iter(corridas.values()))
    m0 = primera["metricas"]
    lineas = [
        f"# Resultados: banco de {banco}, texto «{variante}»", "",
        f"Corrido el {primera['corrido'][:10]} · {m0['casos']} casos ({m0['giros']} giros, {m0['no_giros']} que no "
        f"lo son) · sin tarjeta gráfica, {m0['hilos']} hilos · generado por `evaluar.py`, no se edita a mano.", "",
        "| Modelo | Primeros 5 | Primero | Primeros 10 | Rechazo de no giro | Giros perdidos | Umbral | ms por consulta "
        "| Memoria pico | C1 | C2 | C3 | C4 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    cumplen = 0
    for n, c in corridas.items():
        m, ok = c["metricas"], cumple(c["metricas"])
        cumplen += all(ok.values())
        lineas.append(f"| {n} | {pct(m['primeros_5'])} | {pct(m['primero'])} | {pct(m['primeros_10'])} | "
                      f"{pct(m['rechazo_no_giro'])} | {pct(m['giros_perdidos'])} | {m['umbral']:.3f} | "
                      f"{m['ms_mediana']:.0f} | {m['memoria_pico_gb']:.2f} GB | "
                      + " | ".join("sí" if ok[k] else "no" for k in ("C1", "C2", "C3", "C4")) + " |")
    lineas += ["", "## Acierto entre los primeros 5, por tipo de caso", "",
               "| Modelo | " + " | ".join(NOMBRE_TIPO[t] for t in TIPOS if t != "no_es_giro") + " |",
               "|---|---|---|---|"]
    for n, c in corridas.items():
        por_tipo = c["metricas"]["por_tipo"]
        lineas.append(f"| {n} | " + " | ".join(f"{pct(por_tipo[t]['primeros_5'])} de {por_tipo[t]['casos']}"
                                                for t in TIPOS if t != "no_es_giro") + " |")
    lineas += ["", "## Configuración", ""]
    for n, c in corridas.items():
        lineas.append(f"- **{n}**: `{c['repo']}` revisión `{c['revision'][:10]}` · consulta "
                      f"`{c['instruccion_consulta']!r}` · documento `{c['instruccion_documento']!r}`")
    lineas += ["", "## Fallos (ninguna clase correcta entre los primeros 5)", ""]
    for n, c in corridas.items():
        fallos = [f for f in c["casos"] if f["tipo"] != "no_es_giro" and not (f["posicion"] and f["posicion"] <= 5)]
        lineas.append(f"**{n}** ({len(fallos)}): " + ("; ".join(
            f"«{f['termino']}» → {f['candidatos'][0]['nombre']}" for f in fallos) or "ninguno"))
        lineas.append("")
    ruta = RESULTADOS / f"{banco}-{variante}.md"
    ruta.write_text("\n".join(lineas), encoding="utf-8")
    print(f"escrito {ruta}")
    return cumplen


def main():
    p = argparse.ArgumentParser()
    p.add_argument("banco", choices=["ajuste", "ciego"])
    p.add_argument("--modelo", choices=list(MODELOS))
    p.add_argument("--variante", default="simple", choices=list(VARIANTES))
    p.add_argument("--hilos", type=int, help="hilos de procesador, para parecerse al VPS")
    p.add_argument("--confirmo-ciego", action="store_true")
    a = p.parse_args()

    if a.modelo:  # proceso hijo
        return medir(a.banco, a.variante, a.modelo, a.hilos)

    if a.banco == "ciego":
        if not a.confirmo_ciego:
            raise SystemExit("El banco ciego se corre una sola vez, con los umbrales confirmados. "
                             "Si es el momento, repite con --confirmo-ciego.")
        if (RESULTADOS / "ciego").exists():
            raise SystemExit("El banco ciego ya se corrió (existe resultados/ciego/). No se repite: los fallos pasan "
                             "al banco de ajuste y se escribe un banco ciego nuevo.")
    leer_banco(a.banco)
    nombres = [n for n in MODELOS if rutas(n, a.variante)[0].exists()]
    if a.banco == "ciego":
        # Qwen3 no cumple C1, C3 ni C4 en el ajuste con ninguna variante: no gana aunque mejore en el ciego,
        # así que no se gasta el único intento del banco ciego en él (decisión del 15 nov 2026).
        nombres = [n for n in nombres if n not in EXCLUIDOS_CIEGO]
        if not nombres:
            raise SystemExit("No quedan modelos para el banco ciego.")
    if not nombres:
        raise SystemExit(f"No hay vectores con la variante «{a.variante}». Corre: uv run python vectorizar.py "
                         f"--variante {a.variante}")
    for nombre in nombres:
        orden = [sys.executable, __file__, a.banco, "--modelo", nombre, "--variante", a.variante]
        subprocess.run(orden + (["--hilos", str(a.hilos)] if a.hilos else []), check=True)
    cumplen = comparar(a.banco, a.variante, nombres)
    if a.banco == "ciego" and not cumplen:
        raise SystemExit("Ningún modelo cumple C1–C4 en el banco ciego.")


if __name__ == "__main__":
    main()

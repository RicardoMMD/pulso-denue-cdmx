"""Mide la herramienta completa (glosario, lugar, embeddings y Haiku) contra un banco.

Uso:
  uv run python evaluar_herramienta.py ajuste
  uv run python evaluar_herramienta.py ciego --confirmo-ciego     UNA sola vez

Las respuestas de Haiku se guardan en cache_haiku.json: repetir una corrida no vuelve a llamar al modelo.
Escribe resultados/herramienta/<banco>.json (lo lee el laboratorio) y resultados/herramienta-<banco>.md.
Termina con error si se corre el banco ciego y no se cumplen los criterios.
"""
import argparse
import json
import statistics
import sys
import time
from collections import Counter
from datetime import datetime

from comun import NOMBRE_TIPO, RESULTADOS, TIPOS, leer_banco
from traducir_giro import MODELO_EMB, MODELO_HAIKU, VARIANTE, VERSION_PROMPT, TraductorGiro

# Los mismos umbrales del README (confirmados el 15 nov 2026), ahora sobre la herramienta completa.
C1_ACIERTO = 0.85
C2_POR_TIPO = 0.70
C3_RECHAZO, C3_PERDIDA_MAX = 0.80, 0.05
CON_CLASES = ("resuelto", "grupo", "ambiguo")
SALIDA = RESULTADOS / "herramienta"


def parte(n, total):
    return round(n / total, 4) if total else None


def pct(x):
    return "—" if x is None else f"{100 * x:.0f} %"


def medir(banco):
    casos = leer_banco(banco)["casos"]
    traductor = TraductorGiro()
    traductor.candidatos("calentamiento")
    filas = []
    for caso in casos:
        inicio = time.perf_counter()
        llamadas = traductor.llamadas_modelo
        r = traductor.traducir(caso["termino"])
        ms = (time.perf_counter() - inicio) * 1000
        devueltas = [c["clase"] for c in r["clases"]]
        es_giro = caso["tipo"] != "no_es_giro"
        if es_giro:
            acierta = r["estado"] in CON_CLASES and any(c in caso["clases"] for c in devueltas)
        else:
            acierta = r["estado"] in ("no_es_giro", "sin_resultado")
        filas.append({
            "termino": caso["termino"], "tipo": caso["tipo"], "esperadas": caso["clases"],
            "estado": r["estado"], "capa": r["capa"], "confianza": r["confianza"], "nota": r["nota"],
            "clases": r["clases"], "candidatos": r["candidatos"], "acierta": acierta,
            "limpio": acierta and all(c in caso["clases"] for c in devueltas),
            "perdido": es_giro and r["estado"] not in CON_CLASES,
            "ms": round(ms, 1), "llamo_modelo": traductor.llamadas_modelo > llamadas,
        })
    traductor.guardar_cache()

    giros = [f for f in filas if f["tipo"] != "no_es_giro"]
    no_giros = [f for f in filas if f["tipo"] == "no_es_giro"]
    locales = [f["ms"] for f in filas if not f["llamo_modelo"]]
    metricas = {
        "casos": len(filas), "giros": len(giros), "no_giros": len(no_giros),
        "acierto": parte(sum(f["acierta"] for f in giros), len(giros)),
        "limpio": parte(sum(f["limpio"] for f in giros), len(giros)),
        "por_tipo": {t: {"casos": len(g), "acierto": parte(sum(f["acierta"] for f in g), len(g))}
                     for t in TIPOS if t != "no_es_giro" for g in [[f for f in giros if f["tipo"] == t]]},
        "rechazo_no_giro": parte(sum(f["acierta"] for f in no_giros), len(no_giros)),
        "giros_perdidos": parte(sum(f["perdido"] for f in giros), len(giros)),
        "por_capa": {capa: {"casos": n, "aciertos": sum(f["acierta"] for f in filas if f["capa"] == capa)}
                     for capa, n in Counter(f["capa"] for f in filas).items()},
        "ms_mediana_sin_llamada": round(statistics.median(locales), 1) if locales else None,
        "llamadas_modelo_nuevas": traductor.llamadas_modelo,
    }
    m = metricas
    cumple = {
        "C1": m["acierto"] >= C1_ACIERTO,
        "C2": all(t["acierto"] is not None and t["acierto"] >= C2_POR_TIPO for t in m["por_tipo"].values()),
        "C3": m["rechazo_no_giro"] >= C3_RECHAZO and m["giros_perdidos"] <= C3_PERDIDA_MAX,
    }
    salida = {"banco": banco, "corrido": datetime.now().isoformat(timespec="seconds"),
              "configuracion": {"embeddings": MODELO_EMB, "variante": VARIANTE, "modelo": MODELO_HAIKU,
                                "version_prompt": VERSION_PROMPT, "entradas_glosario": len(traductor.glosario)},
              "metricas": metricas, "cumple": cumple, "casos": filas}
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / f"{banco}.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    lineas = [
        f"# Herramienta completa: banco de {banco}", "",
        f"Corrido el {salida['corrido'][:10]} · {m['casos']} casos ({m['giros']} giros, {m['no_giros']} que no lo son) · "
        f"glosario, lugar, {MODELO_EMB} ({VARIANTE}) y {MODELO_HAIKU} · generado por `evaluar_herramienta.py`, "
        "no se edita a mano.", "",
        "Acierto: la herramienta devuelve al menos una clase aceptable. Limpio: además, todas las que devuelve lo son.",
        "",
        "| Medida | Resultado | Criterio | Cumple |", "|---|---|---|---|",
        f"| Acierto en giros | {pct(m['acierto'])} | C1: al menos {pct(C1_ACIERTO)} | {'sí' if cumple['C1'] else 'no'} |",
        "| Acierto por tipo | " + ", ".join(f"{NOMBRE_TIPO[t].lower()} {pct(v['acierto'])} de {v['casos']}"
                                            for t, v in m["por_tipo"].items())
        + f" | C2: al menos {pct(C2_POR_TIPO)} en cada tipo | {'sí' if cumple['C2'] else 'no'} |",
        f"| Rechazo de lo que no es giro | {pct(m['rechazo_no_giro'])}, con {pct(m['giros_perdidos'])} de giros perdidos "
        f"| C3: al menos {pct(C3_RECHAZO)}, perdiendo máximo {pct(C3_PERDIDA_MAX)} | {'sí' if cumple['C3'] else 'no'} |",
        f"| Respuestas limpias | {pct(m['limpio'])} | se reporta, no decide | |", "",
        "## Qué resolvió cada capa", "", "| Capa | Casos | Aciertos |", "|---|---|---|",
        *[f"| {capa} | {v['casos']} | {v['aciertos']} |" for capa, v in sorted(m["por_capa"].items())], "",
        "## Fallos", "",
    ]
    for f in filas:
        if not f["acierta"]:
            devolvio = ", ".join(c["nombre"] for c in f["clases"]) or "nada"
            lineas.append(f"- «{f['termino']}» ({f['tipo']}, capa {f['capa']}): estado `{f['estado']}`, devolvió {devolvio}")
    (RESULTADOS / f"herramienta-{banco}.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"{banco}: acierto {pct(m['acierto'])}, rechazo {pct(m['rechazo_no_giro'])}, perdidos "
          f"{pct(m['giros_perdidos'])}, llamadas nuevas al modelo {m['llamadas_modelo_nuevas']} · "
          + " ".join(f"{k}={'sí' if v else 'no'}" for k, v in cumple.items()))
    return all(cumple.values())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("banco", choices=["ajuste", "ciego"])
    p.add_argument("--confirmo-ciego", action="store_true")
    a = p.parse_args()
    if a.banco == "ciego":
        if not a.confirmo_ciego:
            raise SystemExit("El banco ciego se corre una sola vez. Si es el momento, repite con --confirmo-ciego.")
        if (SALIDA / "ciego.json").exists():
            raise SystemExit("El banco ciego ya se corrió con la herramienta (existe resultados/herramienta/ciego.json).")
    cumple = medir(a.banco)
    if a.banco == "ciego" and not cumple:
        sys.exit("La herramienta no cumple los criterios en el banco ciego.")


if __name__ == "__main__":
    main()

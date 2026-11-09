"""Evalúa el resolutor contra casos_prueba.json y escribe resultados.md.

Un caso pasa si coinciden el estado y, cuando se declaran, el tipo del primer candidato, los nombres esperados
(deben estar entre los candidatos), la relación y el radio. Uso (túnel abierto, .env cargado):
  uv run python evaluar.py
"""
import json, os, sys, time
from pathlib import Path
import psycopg
from resolver_lugar import resolver_lugar, normalizar

AQUI = Path(__file__).parent
ARCHIVO = sys.argv[1] if len(sys.argv) > 1 else "casos_prueba.json"
SALIDA = sys.argv[2] if len(sys.argv) > 2 else "resultados.md"
casos = json.loads((AQUI / ARCHIVO).read_text(encoding="utf-8"))
conn = psycopg.connect(host=os.environ["PGHOST"], port=os.environ["PGPORT"], dbname=os.environ["PGDATABASE"],
                       user=os.environ.get("PULSO_ANALISTA_USER") or os.environ["PULSO_OWNER_USER"],
                       password=os.environ.get("PULSO_ANALISTA_PASSWORD") or os.environ["PULSO_OWNER_PASSWORD"])
filas, fallas, tiempos = [], [], []
for c in casos:
    t0 = time.perf_counter()
    r = resolver_lugar(conn, c["consulta"])
    tiempos.append((time.perf_counter() - t0) * 1000)
    motivos = []
    if "estado_en" in c:
        if r["estado"] not in c["estado_en"]:
            motivos.append(f"estado {r['estado']} (esperado uno de {c['estado_en']})")
        c = dict(c, estado=r["estado"])  # el tipo se evalúa como en cualquier caso no ambiguo, pero sin exigir orden
        if "tipo" in c and r["candidatos"] and c["tipo"] not in {x["tipo"] for x in r["candidatos"]}:
            motivos.append(f"ningún candidato de tipo {c['tipo']}")
        c.pop("tipo", None)
    elif r["estado"] != c["estado"]:
        motivos.append(f"estado {r['estado']} (esperado {c['estado']})")
    if "tipo" in c and r["candidatos"]:
        if c["estado"] == "ambiguo":  # en un caso ambiguo el orden no está definido: basta con que el tipo esté entre los candidatos
            if c["tipo"] not in {x["tipo"] for x in r["candidatos"]}:
                motivos.append(f"ningún candidato de tipo {c['tipo']}")
        elif r["candidatos"][0]["tipo"] != c["tipo"]:
            motivos.append(f"tipo {r['candidatos'][0]['tipo']} (esperado {c['tipo']})")
    if "primero_tipo" in c and (not r["candidatos"] or r["candidatos"][0]["tipo"] != c["primero_tipo"]):
        motivos.append(f"el primer candidato debía ser de tipo {c['primero_tipo']}")
    if "nombres" in c:
        hay = {normalizar(x["nombre"]) for x in r["candidatos"]}
        falta = [n for n in c["nombres"] if normalizar(n) not in hay]
        if falta:
            motivos.append(f"faltan {falta}")
    if "relacion" in c and r["relacion"] != c["relacion"]:
        motivos.append(f"relación {r['relacion']} (esperada {c['relacion']})")
    if "radio_m" in c and r.get("radio_m") != c["radio_m"]:
        motivos.append(f"radio {r.get('radio_m')} (esperado {c['radio_m']})")
    ok = not motivos
    filas.append((c, r, ok, motivos))
    if not ok:
        fallas.append((c, r, motivos))

n, ok = len(casos), sum(1 for f in filas if f[2])
lineas = [f"# Resultado del banco de pruebas del resolutor de lugares", "",
          f"**{ok} de {n} casos correctos ({100 * ok / n:.0f} %).** Tiempo por consulta: mediana {sorted(tiempos)[n // 2]:.0f} ms, "
          f"máximo {max(tiempos):.0f} ms.", "", "| # | Consulta | Esperado | Obtenido | |", "| --- | --- | --- | --- | --- |"]
for c, r, o, m in filas:
    nombres = ", ".join(x["nombre"] for x in r["candidatos"][:3]) + ("…" if len(r["candidatos"]) > 3 else "")
    esp = (c.get("estado") or "/".join(casos[c["id"] - 1].get("estado_en", []))) + (f" · {casos[c['id'] - 1]['tipo']}" if "tipo" in casos[c["id"] - 1] else "")
    lineas.append(f"| {c['id']} | {c['consulta'] or '(vacía)'} | {esp} | {r['estado']} · {nombres or '—'} | {'✓' if o else '✗ ' + '; '.join(m)} |")
(AQUI / SALIDA).write_text("\n".join(lineas) + "\n", encoding="utf-8")
print(f"{ok}/{n} correctos; mediana {sorted(tiempos)[n // 2]:.0f} ms")
for c, r, m in fallas:
    print(f"  ✗ #{c['id']} {c['consulta']!r}: {'; '.join(m)}")

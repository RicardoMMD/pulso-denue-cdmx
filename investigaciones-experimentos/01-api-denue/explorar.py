"""Exploración inicial de la API DENUE para CDMX (entidad 09)."""
import collections, json
from denue_api import consulta

def seccion(t): print(f"\n== {t}")

# 1. Conteo por sector (2 dígitos) y total
seccion("Cuantificar: establecimientos por sector SCIAN en CDMX")
filas = consulta("Cuantificar", "0", "09", "0")
sectores = [f for f in filas if len(f["AE"]) == 2]
for f in sorted(sectores, key=lambda f: -int(f["Total"])):
    print(f'  {f["AE"]}  {int(f["Total"]):>7}')
print("  total sectores:", sum(int(f["Total"]) for f in sectores))
print("  claves distintas de AE:", sorted({len(f["AE"]) for f in filas}))

# 2. Búsqueda por cercanía (Zócalo), 500 m
seccion("Buscar: 'fonda' a 500 m del Zócalo")
res = consulta("Buscar", "fonda", "19.4326,-99.1332", "500")
print("  resultados:", len(res))
print("  campos:", list(res[0].keys()) if res else None)
for r in res[:3]: print("  ", json.dumps(r, ensure_ascii=False)[:300])

# 3. Ficha completa de un establecimiento
seccion("Ficha de un establecimiento")
ficha = consulta("Ficha", res[0]["Id"])
print(json.dumps(ficha, ensure_ascii=False, indent=1)[:1500])

# 4. Paginación en BuscarEntidad
seccion("BuscarEntidad: 'restaurante' en CDMX, filas 1-5")
ent = consulta("BuscarEntidad", "restaurante", "09", "1", "5")
print("  filas:", len(ent), "| campos:", list(ent[0].keys()))

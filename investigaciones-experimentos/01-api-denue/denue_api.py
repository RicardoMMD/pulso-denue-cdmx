"""Cliente mínimo de la API DENUE de INEGI, con caché en disco.

Token: variable DENUE_API_TOKEN (se lee del .env de la raíz del repo).
Documentación: https://www.inegi.org.mx/servicios/api_denue.html
"""
import json, os, pathlib, time, urllib.parse, urllib.request

BASE = "https://www.inegi.org.mx/app/api/denue/v1/consulta"
RAIZ = pathlib.Path(__file__).resolve().parents[2]
CACHE = pathlib.Path(__file__).with_name("cache")


def _token():
    if os.environ.get("DENUE_API_TOKEN"):
        return os.environ["DENUE_API_TOKEN"]
    for linea in (RAIZ / ".env").read_text().splitlines():
        if linea.startswith("DENUE_API_TOKEN="):
            return linea.split("=", 1)[1].strip()
    raise SystemExit("Falta DENUE_API_TOKEN en .env")


def consulta(metodo, *partes):
    """GET {BASE}/{metodo}/{partes...}/{token}. Devuelve JSON; cachea por URL sin token."""
    ruta = "/".join([metodo, *[urllib.parse.quote(str(p), safe=",") for p in partes]])
    CACHE.mkdir(exist_ok=True)
    archivo = CACHE / (ruta.replace("/", "__") + ".json")
    if archivo.exists():
        return json.loads(archivo.read_text())
    req = urllib.request.Request(f"{BASE}/{ruta}/{_token()}", headers={"User-Agent": "pulso-denue/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        datos = json.loads(r.read().decode("utf-8"))
    archivo.write_text(json.dumps(datos, ensure_ascii=False))
    time.sleep(0.3)
    return datos

"""Genera docs/vista_contenido_descargado.html: una vista elemental de lo que hay en data/raw.

Lee los archivos descargados (no la base de datos) y escribe un HTML autocontenido con inventario,
muestras de filas y un mapa de capas. Uso: python3 generar_vista_descargas.py
"""
import csv, glob, json, math, os, pathlib, random, zipfile

RAIZ = pathlib.Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
SALIDA = RAIZ / "docs" / "vista_contenido_descargado.html"
random.seed(7)


def mb(ruta):
    return round(os.path.getsize(ruta) / 1e6, 1)


def rdp(pts, tol):
    """Ramer-Douglas-Peucker iterativo sobre [(x, y)]."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    pila = [(0, len(pts) - 1)]
    while pila:
        a, b = pila.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        norma = math.hypot(dx, dy) or 1e-12
        mejor, idx = 0, None
        for i in range(a + 1, b):
            d = abs(dy * (pts[i][0] - x1) - dx * (pts[i][1] - y1)) / norma
            if d > mejor:
                mejor, idx = d, i
        if mejor > tol and idx is not None:
            keep[idx] = True
            pila += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def redondear(pts):
    return [[round(x, 4), round(y, 4)] for x, y in pts]


# ---- DENUE ------------------------------------------------------------------
ediciones = [("2024-05", "anterior/0524", "2024-05-23"), ("2024-11", "anterior/1124", "2024-11-26"),
             ("2025-05", "anterior/0525", "2025-05-22"), ("2026-05", "vigente", "2026-05-20")]
denue = []
muestra_puntos, muestra_filas = [], []
for ed, carpeta, pub in ediciones:
    ruta = RAW / carpeta / "conjunto_de_datos" / "denue_inegi_09_.csv"
    n, fuera = 0, 0
    with open(ruta, encoding="latin-1", newline="") as f:
        for r in csv.DictReader(f):
            n += 1
            if ed == "2026-05":
                lat, lon = float(r["latitud"]), float(r["longitud"])
                if 19.0 <= lat <= 19.65 and -99.40 <= lon <= -98.90:
                    if random.random() < 0.035:
                        muestra_puntos.append([round(lon, 5), round(lat, 5), r["codigo_act"][:2]])
                else:
                    fuera += 1
                if n <= 12 or (n % 40000 == 0 and len(muestra_filas) < 20):
                    muestra_filas.append({k: r[k].strip() for k in
                                          ["id", "nom_estab", "codigo_act", "nombre_act", "per_ocu", "nomb_asent",
                                           "municipio", "cod_postal", "latitud", "longitud", "fecha_alta"]})
    denue.append({"edicion": ed, "publicacion": pub, "filas": n, "mb": mb(ruta), "fuera": fuera})
denue[-1]["fuera_nota"] = "puntos fuera de CDMX en esta edición"

# ---- Colonias ---------------------------------------------------------------
colonias = json.load(open(RAW / "externas/colonias.geojson"))["features"]
col_geom, col_tabla = [], []
for f in colonias:
    g = f["geometry"]
    anillos = g["coordinates"] if g["type"] == "Polygon" else [a for p in g["coordinates"] for a in p]
    simp = [redondear(rdp([(p[0], p[1]) for p in a], 0.0002)) for a in anillos[:1] if len(a) > 3]
    col_geom += simp
    p = f["properties"]
    col_tabla.append([p["cve_col"], p["colonia"], p["alc"], p["clasif"]])

# ---- Mercados ---------------------------------------------------------------
mercados = json.load(open(RAW / "externas/mercados.geojson"))["features"]
mer_pts = [[round(f["geometry"]["coordinates"][0], 5), round(f["geometry"]["coordinates"][1], 5),
            f["properties"]["MERCADO"], f["properties"]["TIPO"], f["properties"]["NUM_LOCALE"]] for f in mercados]

# ---- Censo Económico --------------------------------------------------------
ce_ruta = RAW / "externas/ce2024_cdmx/conjunto_de_datos/tr_ce_cdmx_2024.csv"
ce = list(csv.DictReader(open(ce_ruta, encoding="utf-8-sig")))
nombres_mun = {}
for r in csv.DictReader(open(RAW / "externas/ce2024_cdmx/catalogos/tc_entidad_municipio.csv", encoding="utf-8-sig")):
    if r["E03"] == "09":
        nombres_mun[r["E04"]] = r["NOM_MUN"]
nombres_act = {r["CODIGO"].strip(): r["DESC_CODIGO"].strip() for r in
               csv.DictReader(open(RAW / "externas/ce2024_cdmx/catalogos/tc_codigo_actividad.csv", encoding="utf-8-sig"))}
ce_total = [r for r in ce if not r["E04"].strip() and not r["SECTOR"].strip() and not r["ID_ESTRATO"].strip()][0]
ce_sector = sorted(
    [[r["SECTOR"].strip(), nombres_act.get(r["SECTOR"].strip(), ""), int(r["UE"]), int(float(r["H001A"] or 0))]
     for r in ce if r["E04"].strip() and not r["E04"].strip() == "" and r["SECTOR"].strip() and not r["SUBSECTOR"].strip()
     and not r["ID_ESTRATO"].strip()], key=lambda x: x[0])
agg = {}
for s, nombre, ue, po in ce_sector:
    a = agg.setdefault(s, [s, nombre, 0, 0])
    a[2] += ue
    a[3] += po
ce_por_sector = sorted(agg.values(), key=lambda x: -x[2])
ce_por_alcaldia = {}
for r in ce:
    if r["E04"].strip() and not r["SECTOR"].strip() and not r["ID_ESTRATO"].strip():
        ce_por_alcaldia[nombres_mun.get(r["E04"].strip(), r["E04"])] = [int(r["UE"]), int(float(r["H001A"] or 0))]
ce_muestra = [{k: r[k] for k in ["E04", "SECTOR", "SUBSECTOR", "RAMA", "CODIGO", "ID_ESTRATO", "UE", "H001A", "A131A", "A800A"]}
              for r in ce if r["SUBSECTOR"].strip() and r["E04"].strip()][:14]

# ---- OSM calles -------------------------------------------------------------
mosaicos = sorted(glob.glob(str(RAW / "externas/osm/calles_*.json")))
ways = {}
for m in mosaicos:
    for e in json.load(open(m))["elements"]:
        if e["type"] == "way" and e.get("geometry"):
            ways[e["id"]] = e
principales = {"motorway", "trunk", "primary", "secondary", "tertiary", "motorway_link", "trunk_link", "primary_link"}
conteo_tipo, calles_geom, con_nombre = {}, [], 0
for e in ways.values():
    t = e.get("tags", {})
    h = t.get("highway", "?")
    conteo_tipo[h] = conteo_tipo.get(h, 0) + 1
    if "name" in t:
        con_nombre += 1
    if h in principales or random.random() < 0.06:
        pts = [(p["lon"], p["lat"]) for p in e["geometry"] if p]
        pts = rdp(pts, 0.00012)
        if len(pts) >= 2:
            calles_geom.append([1 if h in principales else 0, redondear(pts)])
osm_muestra = [{"osm_id": e["id"], "highway": e["tags"].get("highway"), "name": e["tags"].get("name"),
                "oneway": e["tags"].get("oneway"), "maxspeed": e["tags"].get("maxspeed"),
                "puntos": len(e["geometry"]), "otras_etiquetas": len(e["tags"]) - 1}
               for e in list(ways.values())[:: max(1, len(ways) // 14)][:14]] if ways else []

# ---- PDFs y otros archivos --------------------------------------------------
otros = []
for ruta in sorted(glob.glob(str(RAW / "externas/*.*"))):
    otros.append([pathlib.Path(ruta).name, mb(ruta)])

datos = {
    "denue": denue, "denue_filas": muestra_filas, "denue_puntos": muestra_puntos,
    "col_geom": col_geom, "col_tabla": col_tabla[:25], "col_total": len(colonias),
    "mercados": mer_pts,
    "ce_total": {"ue": int(ce_total["UE"]), "po": int(float(ce_total["H001A"])), "filas": len(ce)},
    "ce_sector": ce_por_sector, "ce_alcaldia": ce_por_alcaldia, "ce_muestra": ce_muestra,
    "osm": {"mosaicos": len(mosaicos), "ways": len(ways), "con_nombre": con_nombre, "tipos": conteo_tipo,
            "mb": round(sum(os.path.getsize(m) for m in mosaicos) / 1e6, 1)},
    "calles": calles_geom, "osm_muestra": osm_muestra, "otros": otros,
}

plantilla = (pathlib.Path(__file__).with_name("vista_descargas.plantilla.html")).read_text(encoding="utf-8")
SALIDA.write_text(plantilla.replace("/*DATOS*/null", json.dumps(datos, ensure_ascii=False, separators=(",", ":"))),
                  encoding="utf-8")
print(f"{SALIDA} ({mb(SALIDA)} MB): {len(muestra_puntos)} puntos DENUE, {len(col_geom)} anillos de colonia, "
      f"{len(calles_geom)} calles dibujadas de {len(ways)} ({len(mosaicos)} mosaicos)")

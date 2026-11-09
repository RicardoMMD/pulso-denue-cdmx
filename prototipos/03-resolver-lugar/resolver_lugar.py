"""Herramienta "Resolver lugar" del Analista (prototipo 3).

Convierte una forma coloquial de nombrar un lugar de la Ciudad de México ("la Roma", "cerca del metro Balderas",
"a 10 minutos del Zócalo", "Iztapalpa") en identificadores territoriales que el resto del sistema entiende.

Es determinista y sin modelo de lenguaje: lee solo `semantic.lugar` (la superficie autorizada) y un glosario de
alias propio de CDMX (`glosario.json`). Cuando no logra resolver, lo dice; nunca inventa un lugar.

Resultado (diccionario):
  consulta, normalizada
  estado     resuelto | grupo | ambiguo | sin_resultado | fuera_de_cdmx
  relacion   en | cerca_de
  radio_m    solo con cerca_de
  ancla      {latitud, longitud} del punto de referencia (cerca_de)
  candidatos [{tipo, clave, nombre, alcaldia, latitud, longitud, puntaje, metodo}]
  confianza  alta | media | baja
  nota       texto para el usuario cuando hay algo que aclarar
"""
from __future__ import annotations

import difflib
import json
import re
import unicodedata
from pathlib import Path

GLOSARIO = json.loads((Path(__file__).parent / "glosario.json").read_text(encoding="utf-8"))
FUERA = set(GLOSARIO["fuera_de_cdmx"])

PRIORIDAD_TIPO = {"ciudad": 0, "alcaldia": 1, "colonia": 2, "estacion_metro": 3, "conglomerado": 4, "calle": 5}
RADIO_POR_TIPO = {"estacion_metro": 500, "conglomerado": 300, "calle": 300, "colonia": 800}
METROS_POR_MINUTO = 80  # caminando, en línea recta
UMBRAL_FUZZY = 0.42
ARTICULOS = {"LA", "EL", "LOS", "LAS", "DE", "DEL", "AL", "UN", "UNA", "A", "EN", "POR", "CON"}
DEIXIS = {"MI CASA", "MI TRABAJO", "MI OFICINA", "MI ESCUELA", "MI COLONIA", "MI ALCALDIA", "MI BARRIO", "MI CALLE", "AQUI",
          "ACA", "DONDE VIVO", "DONDE TRABAJO", "DONDE ESTOY", "MI ZONA", "MI UBICACION", "MI NEGOCIO"}
GENERICAS = {"MERCADO", "PLAZA", "CENTRAL", "TIANGUIS", "CALLE", "AVENIDA", "AV", "EJE", "CALZADA", "CALZ", "BOULEVARD", "BLVD",
            "CIRCUITO", "PASEO", "COLONIA", "ALCALDIA", "METRO", "ESTACION", "CERRADA", "PROLONGACION", "ANDADOR", "PRIVADA"}
UMBRAL_NUCLEO = 0.72  # parecido mínimo del nombre sin palabras genéricas, para aceptar una coincidencia aproximada
VACIAS = {"LA", "EL", "LOS", "LAS", "DE", "DEL", "Y", "AL"}  # se ignoran al comparar conjuntos de palabras
TERRITORIALES = ("ciudad", "alcaldia", "colonia")

PREFIJOS_TIPO = [  # (patrón sobre texto normalizado, tipo, conservar el prefijo en el nombre)
    (r"^(?:ESTACION(?: DEL| DE LA)? METRO|ESTACION|METRO|STC)\s+", "estacion_metro", False),
    (r"^(?:COLONIA|COL)\s+", "colonia", False),
    (r"^(?:ALCALDIA|DELEGACION)\s+", "alcaldia", False),
    (r"^(?:CALLE|AVENIDA|AV|AVE|EJE|CALZADA|CALZ|BOULEVARD|BLVD|CIRCUITO|PASEO)\s+", "calle", True),
    (r"^(?:MERCADO|PLAZA|CENTRAL|TIANGUIS)\s+", "conglomerado", True),
]

RELACION_CERCA = re.compile(
    r"^(?:A\s+(?P<n>\d+(?:\s\d+)?)\s*(?P<u>METROS|METRO|M|KILOMETROS|KILOMETRO|KM|MINUTOS|MINUTO|MIN)\s+"
    r"(?:CAMINANDO\s+|A PIE\s+)?(?:DE|DEL)\s+"
    r"|(?:CERCA|CERQUITA|CERCANO|CERCANOS|ALREDEDOR|ALREDEDORES|JUNTO|PEGADO|PEGADITO|COLINDANDO|POR)\s+(?:DE\s+|DEL\s+|A\s+|AL\s+)?)"
    r"(?P<resto>.+)$")
RELACION_EN = re.compile(r"^(?:EN|DENTRO DE|DE|DEL|SOBRE)\s+(?P<resto>.+)$")
LINEA_METRO = re.compile(r"^(?:LA\s+)?LINEA\s+(?P<l>\d{1,2}|A|B)(?:\s+DEL\s+METRO)?$|^(?:EL\s+)?METRO\s+LINEA\s+(?P<l2>\d{1,2}|A|B)$")


def normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto or "")
    t = "".join(c for c in t if not unicodedata.combining(c)).upper()
    t = re.sub(r"[^A-Z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _quitar_articulos(t: str) -> str:
    palabras = t.split()
    while palabras and palabras[0] in ARTICULOS:
        palabras.pop(0)
    return " ".join(palabras)


def _variantes(con_articulo: str, sin_articulos: str) -> list[str]:
    """Del más específico al más general: "LA DEL VALLE" -> ["LA DEL VALLE", "DEL VALLE", "VALLE"]."""
    out, palabras = [con_articulo], con_articulo.split()
    if palabras and palabras[0] in ARTICULOS:
        out.append(" ".join(palabras[1:]))
    out.append(sin_articulos)
    vistos = []
    for v in out:
        if v and v not in vistos:
            vistos.append(v)
    return vistos


def texto_para_calle(texto: str) -> str:
    """El texto de la consulta sin la relación espacial inicial ("cerca de ..."), para recuperar el nombre de la calle tal cual."""
    t = normalizar(texto)
    m = RELACION_CERCA.match(t)
    return m.group("resto") if m else t


def interpretar(texto: str) -> dict:
    """Separa relación espacial, radio, pista de tipo y nombre del lugar. No consulta la base."""
    norm = normalizar(texto)
    norm = re.sub(r"^(?:EN\s+)?(?:TODA|TODO|TODAS|TODOS)\s+(?:LA\s+|EL\s+|LOS\s+|LAS\s+)?(?=\w)", "", norm)  # "toda la CDMX"
    relacion, radio, resto = "en", None, norm
    m = RELACION_CERCA.match(norm)
    if m:
        relacion, resto = "cerca_de", m.group("resto")
        if m.group("n"):
            n = float(m.group("n").replace(" ", "."))
            u = m.group("u")
            radio = n * (1000 if u.startswith("K") else METROS_POR_MINUTO if u.startswith("MIN") else 1)
    else:
        m = RELACION_EN.match(norm)
        if m:
            resto = m.group("resto")
    con_articulo = resto
    resto = _quitar_articulos(resto)
    tipo, fuerte, sin_prefijo = None, False, ""
    mlinea = LINEA_METRO.match(resto) or LINEA_METRO.match(norm)
    if mlinea:
        return {"relacion": relacion, "radio_m": radio, "tipo": "linea_metro", "nombre": (mlinea.group("l") or mlinea.group("l2")),
                "resto": resto, "variantes": [resto]}
    for patron, t, conservar in PREFIJOS_TIPO:
        mp = re.match(patron, resto)
        if mp and len(resto) > mp.end():
            tipo, fuerte = t, not conservar  # "metro X" es una pista firme; "mercado"/"plaza" ya forman parte del nombre
            sin_prefijo = _quitar_articulos(resto[mp.end():])
            con_articulo = resto[mp.end():] if not conservar else resto
            if not conservar:
                resto = sin_prefijo
            break
    variantes = _variantes(con_articulo, resto)
    if tipo == "calle":  # el catálogo guarda la calle sin el tipo de vía y a veces con la preposición ("DE TLALPAN")
        crudo = re.sub(PREFIJOS_TIPO[3][0], "", normalizar(texto_para_calle(texto)))
        for v in (crudo, sin_prefijo):
            if v and v not in variantes:
                variantes.append(v)
    return {"relacion": relacion, "radio_m": radio, "tipo": tipo, "nombre": resto, "resto": resto,
            "variantes": variantes, "fuerte": fuerte}


def _fila(r, puntaje, metodo):
    peso = r[8] if len(r) > 8 else r[7]
    return {"tipo": r[0], "clave": r[1], "nombre": r[2], "alcaldia": r[3], "latitud": r[4], "longitud": r[5],
            "puntaje": round(float(puntaje), 3), "metodo": metodo, "peso": float(peso or 0)}


SQL_BASE = "select tipo, clave, nombre, alcaldia, latitud, longitud, nombre_norm, peso from semantic.lugar"


def _nucleo(t: str) -> str:
    return " ".join(w for w in t.split() if w not in GENERICAS and w not in VACIAS)


def _parecido_nucleo(a: str, b: str) -> float:
    """Parecido de los nombres sin palabras genéricas ("PLAZA", "AVENIDA"), que inflan la similitud de trigramas."""
    na, nb = _nucleo(a), _nucleo(b)
    if not na or not nb:  # el nombre entero es genérico ("Eje Central"): comparar completo
        na, nb = a, b
    return difflib.SequenceMatcher(None, na, nb).ratio()


def _buscar(conn, nombre: str, tipo: str | None, variantes: list[str] | None = None):
    """Devuelve (candidatos, metodo) en el primer método que produzca resultados."""
    filtro_t = " and tipo = %(tipo)s" if tipo else ""
    p = {"n": nombre, "tipo": tipo}
    # 1. exacto, de la forma más específica ("El Rosario") a la más general
    for v in (variantes or [nombre]):
        rows = conn.execute(f"{SQL_BASE} where nombre_norm = %(v)s{filtro_t}", {"v": v, "tipo": tipo}).fetchall()
        if rows:
            return [_fila(r, 1.0, "exacto") for r in rows], "exacto"
    # 2. contención de palabras (todas las palabras de la consulta aparecen en el nombre)
    toks = [t for t in nombre.split() if t not in VACIAS]
    if len(nombre) >= 3 and toks:
        p["toks"] = toks
        rows = conn.execute(
            f"{SQL_BASE} where string_to_array(nombre_norm, ' ') @> %(toks)s::text[]{filtro_t}"
            " order by peso desc limit 40", p).fetchall()
        if rows:
            iguales = [r for r in rows if {t for t in r[6].split() if t not in VACIAS} == set(toks)]
            if iguales:  # mismo conjunto de palabras, ignorando artículos: equivale a un exacto
                return [_fila(r, 1.0, "exacto") for r in iguales], "exacto"
            return [_fila(r, 0.9, "contiene") for r in rows], "contiene"
    # 3. aproximado (errores de dedo, variantes de escritura)
    if not _nucleo(nombre):  # un nombre solo de palabras genéricas ("Eje Central") no se acepta por parecido
        return [], None
    rows = conn.execute(
        f"select tipo, clave, nombre, alcaldia, latitud, longitud, nombre_norm, similarity(nombre_norm, %(n)s) s, peso "
        f"from semantic.lugar where nombre_norm %% %(n)s{filtro_t} order by s desc, peso desc limit 6", p).fetchall()
    rows = [r for r in rows if r[7] >= UMBRAL_FUZZY and _parecido_nucleo(nombre, r[6]) >= UMBRAL_NUCLEO]
    if rows:
        rows = [r for r in rows if r[7] >= rows[0][7] - 0.08]
        return [_fila(r, r[7], "aproximado") for r in rows], "aproximado"
    return [], None


def _por_glosario(conn, variantes: list[str], tipo: str | None = None):
    ent = next((GLOSARIO["alias"][v] for v in variantes if v in GLOSARIO["alias"]), None)
    if not ent:
        return None, None
    out = []
    for d in ent["destinos"]:
        if tipo and d["tipo"] != tipo:
            continue  # la pista ("metro Tepito") manda sobre el glosario
        sql = f"{SQL_BASE} where tipo = %(t)s and nombre_norm = %(n)s"
        p = {"t": d["tipo"], "n": d["nombre_norm"]}
        if d.get("alcaldia_norm"):
            sql += " and upper(unaccent(alcaldia)) = %(a)s"
            p["a"] = d["alcaldia_norm"]
        out += [_fila(r, 1.0, "glosario") for r in conn.execute(sql, p).fetchall()]
    return out, ent.get("nota")


def _priorizar(cands: list[dict]):
    """Si entre los candidatos hay territorios (ciudad, alcaldía, colonia), solo el tipo territorial de mayor
    jerarquía cuenta: "Coyoacán" es la alcaldía aunque exista una calle Coyoacán. Los demás pasan a `otros`."""
    terr = [c for c in cands if c["tipo"] in TERRITORIALES]
    if terr and len(terr) < len(cands):
        mejor = min(PRIORIDAD_TIPO[c["tipo"]] for c in terr)
        elegidos = [c for c in terr if PRIORIDAD_TIPO[c["tipo"]] == mejor]
        return elegidos, [c for c in cands if c not in elegidos]
    if terr:
        mejor = min(PRIORIDAD_TIPO[c["tipo"]] for c in terr)
        return [c for c in terr if PRIORIDAD_TIPO[c["tipo"]] == mejor], [c for c in terr if PRIORIDAD_TIPO[c["tipo"]] != mejor]
    return cands, []


def _colapsar_calles(cands: list[dict]) -> list[dict]:
    """Una calle que cruza varias alcaldías es un solo lugar: un candidato con la lista de alcaldías. Los registros
    del catálogo con el mismo tipo, nombre y alcaldía (polígonos partidos) también son un solo lugar."""
    out, por_nombre, vistos = [], {}, {}
    for c in sorted(cands, key=lambda c: -c["puntaje"]):
        if c["tipo"] != "calle":
            k = (c["tipo"], c["nombre"], c["alcaldia"])
            if k in vistos:
                vistos[k].setdefault("claves", [vistos[k]["clave"]]).append(c["clave"])
                continue
            vistos[k] = c
            out.append(c)
        elif c["nombre"] in por_nombre:
            por_nombre[c["nombre"]]["alcaldias"].append(c["alcaldia"])
            por_nombre[c["nombre"]]["peso"] += c["peso"]
        else:
            c = dict(c, alcaldias=[c["alcaldia"]])
            por_nombre[c["nombre"]] = c
            out.append(c)
    return out


def _agrupar(cands: list[dict], metodo: str):
    """Decide si varios candidatos forman un solo lugar (grupo) o son ambiguos."""
    if len(cands) <= 1:
        return ("resuelto" if cands else "sin_resultado"), cands
    tipos = {c["tipo"] for c in cands}
    if metodo == "glosario":
        return "grupo", cands
    if tipos == {"calle"}:  # varias calles de nombre parecido: manda la que tiene mucho más comercio
        orden = sorted(cands, key=lambda c: -c["peso"])
        if orden[0]["peso"] >= 3 * max(orden[1]["peso"], 1):
            return "resuelto", orden[:1]
    if metodo == "contiene" and tipos == {"colonia"} and len({c["alcaldia"] for c in cands}) == 1:
        return "grupo", cands  # p. ej. Roma Norte y Roma Sur, Polanco I a V sección
    if metodo == "contiene" and tipos == {"conglomerado"} and len({c["alcaldia"] for c in cands}) == 1:
        return "grupo", cands  # p. ej. los mercados de La Merced
    if metodo == "contiene" and tipos <= {"colonia", "conglomerado", "calle", "estacion_metro"} and len(tipos) > 1:
        # nombre parcial que cae en varios tipos: el de mayor prioridad lidera, pero es ambiguo
        return "ambiguo", sorted(cands, key=lambda c: (PRIORIDAD_TIPO[c["tipo"]], -c["puntaje"]))
    return "ambiguo", cands


def resolver_lugar(conn, texto: str) -> dict:
    """Resuelve `texto` a lugares de `semantic.lugar`. `conn` es una conexión psycopg con acceso de lectura a semantic."""
    q = interpretar(texto)
    res = {"consulta": texto, "normalizada": q["nombre"], "estado": "sin_resultado", "relacion": q["relacion"],
           "candidatos": [], "confianza": "baja", "nota": None}
    nombre = q["nombre"]
    if not nombre:
        res["nota"] = "No encontré un nombre de lugar en la consulta."
        return res

    if nombre in DEIXIS or q["variantes"][0] in DEIXIS:
        res["nota"] = "No puedo ubicar una referencia personal como \"mi casa\"; dime el nombre de la colonia, calle, estación o alcaldía."
        return res
    cands, nota, metodo = [], None, None
    if q["tipo"] == "linea_metro":
        r = conn.execute("select distinct lineas from semantic.metro_estacion where lineas ~ %(re)s limit 1",
                         {"re": rf"Línea {nombre}\M"}).fetchone()
        if r:
            cands = [{"tipo": "linea_metro", "clave": f"Línea {nombre}", "nombre": f"Línea {nombre}", "alcaldia": None,
                      "latitud": None, "longitud": None, "puntaje": 1.0, "metodo": "patron"}]
            metodo = "patron"
    else:
        cands, nota = _por_glosario(conn, q["variantes"], q["tipo"] if q.get("fuerte") else None)
        metodo = "glosario" if cands else None
        if not cands:
            cands, metodo = _buscar(conn, nombre, q["tipo"], q["variantes"])
        if cands and q["tipo"] is None and metodo == "exacto" and not any(c["tipo"] in TERRITORIALES for c in cands):
            toks = [t for t in nombre.split() if t not in VACIAS]
            terr = conn.execute(
                f"{SQL_BASE} where tipo in ('colonia', 'alcaldia') and string_to_array(nombre_norm, ' ') @> %(t)s::text[] "
                "order by peso desc limit 12", {"t": toks}).fetchall() if toks else []
            if terr:  # "Escandón", "las Portales": la gente habla de la colonia, no del negocio o la estación homónimos
                previos, cands, metodo = cands, [_fila(x, 0.9, "contiene") for x in terr], "contiene"
                res["otros_posibles"] = [{"tipo": c["tipo"], "nombre": c["nombre"], "alcaldia": c["alcaldia"]} for c in previos[:5]]
        if not cands and q["tipo"]:  # la pista de tipo pudo estorbar (p. ej. "Plaza" como parte del nombre)
            cands, metodo = _buscar(conn, q["resto"], None, q["variantes"])
        if ((q["tipo"] is None or all(c["tipo"] != q["tipo"] for c in cands)) and metodo != "glosario" and (nombre in FUERA or set(nombre.split()) & FUERA)
                and not any(c["tipo"] in TERRITORIALES and c["metodo"] == "exacto" for c in cands)):
            # "Toluca" o "Ecatepec": un municipio de fuera. Una calle o estación homónima no basta para llevarlo a CDMX.
            res["otros_posibles"] = [{"tipo": c["tipo"], "nombre": c["nombre"], "alcaldia": c["alcaldia"]} for c in cands[:5]]
            cands, metodo = [], None
        if not cands and not q.get("fuerte"):
            toks = set(nombre.split())
            if nombre in FUERA or toks & FUERA:
                res["estado"] = "fuera_de_cdmx"
                res["nota"] = "Ese lugar está fuera de la Ciudad de México; el DENUE de este portal cubre solo CDMX."
                if res.get("otros_posibles"):
                    res["nota"] += " Si te refieres a un lugar de CDMX con ese nombre (una calle o estación), dilo con el tipo, por ejemplo \"calle Toluca\"."
                return res

    otros = []
    if metodo != "glosario":
        cands, otros = _priorizar(cands)
    cands = _colapsar_calles(cands)
    # errata de una alcaldía ("Cuahutemoc"): si lo exacto no es territorial, ofrecer la alcaldía parecida primero
    if (cands and metodo == "exacto" and not any(c["tipo"] in TERRITORIALES for c in cands) and q["tipo"] in (None, "alcaldia")
            and " " not in nombre and len(nombre) >= 6):
        alc = conn.execute(f"select tipo, clave, nombre, alcaldia, latitud, longitud, nombre_norm, similarity(nombre_norm, %s) s "
                           "from semantic.lugar where tipo = 'alcaldia' order by s desc limit 1", (nombre,)).fetchone()
        if alc and alc[7] >= 0.4:
            cands = [_fila(alc + (0,), alc[7], "aproximado")] + cands
            metodo = "aproximado-mixto"
    estado, cands = _agrupar(cands, metodo or "")
    if metodo == "aproximado-mixto":
        estado = "ambiguo"
    res["estado"], res["candidatos"] = estado, cands
    if otros and "otros_posibles" not in res:
        res["otros_posibles"] = [{"tipo": c["tipo"], "nombre": c["nombre"], "alcaldia": c["alcaldia"]} for c in otros[:5]]
    if estado in ("resuelto", "grupo") and metodo in ("exacto", "glosario", "patron"):
        res["confianza"] = "alta"
    elif estado in ("resuelto", "grupo"):
        res["confianza"] = "media"
    if estado == "ambiguo":
        res["nota"] = "Hay varios lugares con ese nombre; pide al usuario que elija: " + "; ".join(
            f"{c['nombre']} ({c['tipo'].replace('_', ' ')}{', ' + c['alcaldia'] if c['alcaldia'] else ''})" for c in cands[:5])
    if nota:
        res["nota"] = nota
    if estado in ("resuelto", "grupo") and res.get("otros_posibles"):
        res["confianza"] = "media"
        otros_txt = "; ".join(f"{o['nombre']} ({o['tipo'].replace('_', ' ')})" for o in res["otros_posibles"][:3])
        res["nota"] = ((res["nota"] + " ") if res["nota"] else "") + f"También podría referirse a: {otros_txt}."
    if estado in ("resuelto", "grupo") and nombre in FUERA and metodo == "exacto":
        res["nota"] = ((res["nota"] + " ") if res["nota"] else "") + "Ojo: también hay un municipio con ese nombre fuera de CDMX; aquí se entendió el de la ciudad."
    if estado == "resuelto" and cands and cands[0]["tipo"] == "estacion_metro" and q["tipo"] is None and not nota:
        res["nota"] = f"Entendí la estación del Metro {cands[0]['nombre']}."
    if metodo == "aproximado" and estado != "sin_resultado":
        res["nota"] = (res["nota"] + " " if res["nota"] else "") + "Corregí la escritura; confirma que es el lugar que buscas."

    # relación espacial: punto de referencia y radio
    if q["relacion"] == "cerca_de" and cands:
        puntos = [(c["latitud"], c["longitud"]) for c in cands if c["latitud"] is not None]
        if puntos and cands[0]["tipo"] not in ("alcaldia", "ciudad"):
            res["ancla"] = {"latitud": round(sum(p[0] for p in puntos) / len(puntos), 6),
                            "longitud": round(sum(p[1] for p in puntos) / len(puntos), 6)}
            radio = q["radio_m"] or RADIO_POR_TIPO.get(cands[0]["tipo"], 500)
            res["radio_m"] = int(min(max(radio, 100), 3000))
        elif cands[0]["tipo"] in ("alcaldia", "ciudad"):
            res["relacion"] = "en"
            res["nota"] = ((res["nota"] + " ") if res["nota"] else "") + "\"Cerca de\" no aplica a una alcaldía; se usa la alcaldía completa."
    return res

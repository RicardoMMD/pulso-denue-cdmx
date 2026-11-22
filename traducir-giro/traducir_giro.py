"""traducir_giro: forma común de nombrar un giro → clases SCIAN 2023.

Capas, de la más confiable a la más flexible:
  1. Glosario (glosario.json): exacto y, para errores de dedo, por parecido de escritura.
  2. Lugar: si el texto es el nombre de una alcaldía, colonia o estación, no es un giro (le toca a resolver_lugar).
  3. Embeddings (EmbeddingGemma, texto con palabras frecuentes): 10 candidatos. Esta capa no decide.
  4. Modelo (Haiku): elige entre los candidatos, o dice que ninguno o que no es un giro.

Nunca devuelve una clase que no esté en el glosario o entre los candidatos.
Uso suelto: uv run python traducir_giro.py "donde arreglan celulares"   (necesita ANTHROPIC_API_KEY si no está en caché)
"""
from __future__ import annotations

import difflib
import hashlib
import json
import re
import sys
from typing import Literal

from pydantic import BaseModel

from comun import RAIZ, leer_catalogo, normalizar

MODELO_EMB, VARIANTE, CANDIDATOS = "gemma", "palabras", 10
MODELO_HAIKU = "claude-haiku-5-5"
VERSION_PROMPT = "2"          # cambiarla invalida la caché de respuestas (2: regla de reparación, 15 nov 2026)
PARECIDO_GLOSARIO = 0.84      # parecido de escritura mínimo para aceptar un error de dedo (fijado en el ajuste)
RUTA_CACHE = RAIZ / "cache_haiku.json"
# Catálogos del proyecto principal para reconocer lugares, sin base.
RUTA_REFERENCIAS = RAIZ.parent / "backend" / "contracts" / "referencias" / "2026-05.json"
RUTA_ALIAS_LUGAR = RAIZ.parent / "prototipos" / "03-resolver-lugar" / "glosario.json"

ARTICULOS = ("LA ", "EL ", "LOS ", "LAS ", "UNA ", "UN ")
PISTAS_LUGAR = ("COLONIA ", "COL ", "ALCALDIA ", "DELEGACION ", "METRO ", "ESTACION ")

SISTEMA = """Eres parte de un portal sobre los negocios de la Ciudad de México (datos del DENUE de INEGI). \
Recibes un texto tal como lo escribió una persona y una lista de clases SCIAN candidatas. Tu trabajo es decidir \
qué clases corresponden al giro que la persona nombra, para después contar o mostrar esos negocios.

Cómo decidir:
- Elige solo entre los códigos de la lista. Nunca escribas un código que no esté ahí.
- Piensa en el negocio de barrio que la persona busca. Casi siempre es comercio al por menor o un servicio; \
elige fabricación o comercio al por mayor solo si el texto lo pide o si no hay otra opción razonable.
- Si el texto habla de arreglar, componer, reparar o dar mantenimiento, elige la clase de reparación o servicio; \
nunca la de fabricación.
- "Nombres comunes" son palabras frecuentes en los nombres reales de los negocios de esa clase; son buena evidencia.
- Estados:
  - resuelto: una sola clase corresponde.
  - grupo: varias clases juntas forman el giro (por ejemplo, sector privado y público, o variantes del mismo negocio).
  - ambiguo: el texto admite lecturas distintas y conviene preguntar; devuelve las clases de cada lectura.
  - sin_resultado: el texto nombra un giro, pero ninguna clase candidata corresponde.
  - no_es_giro: el texto no nombra una actividad económica (un lugar, un saludo, un adjetivo, una frase suelta, \
una pregunta sobre precio u horario). Devuelve la lista de clases vacía.
- El texto puede traer errores de dedo; interpreta la palabra que la persona quiso escribir.
- En "nota" escribe una frase corta en español para la persona, sin códigos."""


class Eleccion(BaseModel):
    estado: Literal["resuelto", "grupo", "ambiguo", "sin_resultado", "no_es_giro"]
    clases: list[str]
    nota: str


def normalizar_termino(texto: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^A-ZÑ0-9 ]", " ", normalizar(texto))).strip()


def _sin_articulo(t: str) -> str:
    for a in ARTICULOS:
        if t.startswith(a):
            return t[len(a):]
    return t


def _formas(t: str) -> list[str]:
    """El término, sin artículo inicial y en singular simple."""
    formas = [t, _sin_articulo(t)]
    for f in list(formas):
        if len(f) > 5 and f.endswith("S"):
            formas.append(f[:-1])
    return list(dict.fromkeys(formas))


class TraductorGiro:
    def __init__(self, usar_modelo: bool = True):
        self.usar_modelo = usar_modelo
        self.catalogo = {c["clase_scian"]: c for c in leer_catalogo()["clases"]}
        glosario = json.loads((RAIZ / "glosario.json").read_text(encoding="utf-8"))
        self.glosario = {}
        for e in glosario["entradas"]:
            for nombre in [e["termino"], *e.get("variantes", [])]:
                self.glosario[normalizar_termino(nombre)] = e
        self.lugares = self._leer_lugares()
        self.cache = json.loads(RUTA_CACHE.read_text(encoding="utf-8")) if RUTA_CACHE.exists() else {}
        self.llamadas_modelo = 0
        self._emb = self._cliente = None

    @staticmethod
    def _leer_lugares() -> set[str]:
        lugares = set()
        if RUTA_REFERENCIAS.exists():
            ref = json.loads(RUTA_REFERENCIAS.read_text(encoding="utf-8"))["lugares"]
            for tipo in ("ciudad", "alcaldia", "colonia", "estacion_metro"):
                lugares.update(normalizar_termino(n) for n in ref[tipo].values())
        if RUTA_ALIAS_LUGAR.exists():
            lugares.update(json.loads(RUTA_ALIAS_LUGAR.read_text(encoding="utf-8"))["alias"])
        return {l for l in lugares if l}

    # --- capas ---------------------------------------------------------------------------------

    def _por_glosario(self, t: str):
        for f in _formas(t):
            if f in self.glosario:
                return self.glosario[f], "alta", "exacto"
        if len(t) >= 5 and " " not in t:
            cerca = difflib.get_close_matches(t, [k for k in self.glosario if " " not in k], n=2,
                                              cutoff=PARECIDO_GLOSARIO)
            # Un solo parecido claro: si dos entradas distintas quedan igual de cerca, no se adivina.
            if cerca and (len(cerca) == 1 or self.glosario[cerca[0]] is self.glosario[cerca[1]]
                          or difflib.SequenceMatcher(None, t, cerca[0]).ratio()
                          > difflib.SequenceMatcher(None, t, cerca[1]).ratio() + 0.03):
                return self.glosario[cerca[0]], "media", f"parecido a «{self.glosario[cerca[0]]['termino']}»"
        return None

    def _es_lugar(self, t: str) -> bool:
        s = _sin_articulo(t)
        for p in PISTAS_LUGAR:
            if s.startswith(p):
                return _sin_articulo(s[len(p):]) in self.lugares or s[len(p):] in self.lugares
        return t in self.lugares or s in self.lugares

    def candidatos(self, texto: str) -> list[dict]:
        if self._emb is None:
            from buscar import mas_cercanas
            from comun import cargar_modelo, codificar
            from vectorizar import leer_vectores
            codigos, vectores = leer_vectores(MODELO_EMB, VARIANTE)
            modelo = cargar_modelo(MODELO_EMB)
            self._emb = lambda q: mas_cercanas(codificar(modelo, MODELO_EMB, [q], "consulta")[0], codigos, vectores,
                                               CANDIDATOS)
        return [{"clase": c, "parecido": round(p, 4)} for c, p in self._emb(texto)]

    def _elegir(self, texto: str, candidatos: list[dict]) -> dict:
        codigos = [c["clase"] for c in candidatos]
        llave = hashlib.sha256(json.dumps([MODELO_HAIKU, VERSION_PROMPT, texto, codigos]).encode()).hexdigest()[:24]
        if llave not in self.cache:
            import anthropic
            if self._cliente is None:
                self._cliente = anthropic.Anthropic()
            lineas = []
            for c in candidatos:
                k = self.catalogo[c["clase"]]
                comunes = ", ".join(p["palabra"].lower() for p in k.get("palabras_frecuentes", [])[:8])
                lineas.append(f"- {k['clase_scian']} · {k['nombre_clase']} · {k['establecimientos_vigente']} negocios"
                              + (f" · Nombres comunes: {comunes}" if comunes else "")
                              + (f" · Posible corrección de escritura de «{c['escritura_de']}»: elígela solo si el "
                                 "texto parece un error de tecleo de esa palabra, no otra palabra real"
                                 if c.get("escritura_de") else ""))
            r = self._cliente.messages.parse(
                model=MODELO_HAIKU, max_tokens=4000,
                system=[{"type": "text", "text": SISTEMA, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": f"Texto de la persona: «{texto}»\n\nClases candidatas:\n"
                           + "\n".join(lineas)}],
                output_config={"effort": "low"},
                output_format=Eleccion,
            )
            self.llamadas_modelo += 1
            if r.stop_reason == "refusal" or r.parsed_output is None:
                e = Eleccion(estado="sin_resultado", clases=[], nota="No pude interpretar ese giro.")
            else:
                e = r.parsed_output
            self.cache[llave] = {"texto": texto, **e.model_dump()}
        return self.cache[llave]

    def guardar_cache(self):
        RUTA_CACHE.write_text(json.dumps(self.cache, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                              encoding="utf-8")

    # --- la herramienta ------------------------------------------------------------------------

    def _clases(self, codigos):
        return [{"clase": c, "nombre": self.catalogo[c]["nombre_clase"],
                 "establecimientos": self.catalogo[c]["establecimientos_vigente"]} for c in codigos]

    def traducir(self, texto: str) -> dict:
        t = normalizar_termino(texto)
        base = {"consulta": texto, "clases": [], "candidatos": []}
        if not t:
            return {**base, "estado": "no_es_giro", "capa": "glosario", "confianza": "alta", "nota": "No hay texto."}

        hallado = self._por_glosario(t)
        candidatos = None
        if hallado and hallado[1] == "media" and hallado[0]["clases"]:
            # Un parecido solo de escritura se acepta directo si los embeddings lo respaldan. Si no, no se descarta:
            # pasa a Haiku como candidato marcado, que distingue un error de tecleo («feretería») de otra palabra
            # real («pastelería» no es «papelería»; fallo del segundo banco ciego, 15 nov 2026).
            candidatos = self.candidatos(texto)
            codigos = {c["clase"] for c in candidatos}
            if not set(hallado[0]["clases"]) & codigos:
                candidatos += [{"clase": c, "parecido": 0.0, "origen": "glosario",
                                "escritura_de": hallado[0]["termino"]}
                               for c in hallado[0]["clases"] if c not in codigos]
                hallado = None
        if hallado:
            entrada, confianza, como = hallado
            if not entrada["clases"]:
                return {**base, "estado": "no_es_giro", "capa": "glosario", "confianza": confianza,
                        "nota": entrada["nota"]}
            return {**base, "estado": "resuelto" if len(entrada["clases"]) == 1 else "grupo",
                    "clases": self._clases(entrada["clases"]), "capa": "glosario", "confianza": confianza,
                    "nota": entrada.get("nota") or f"Giro del glosario ({como})."}

        if self._es_lugar(t):
            return {**base, "estado": "no_es_giro", "capa": "lugar", "confianza": "alta",
                    "nota": "Es un lugar, no un giro. Para lugares se usa resolver_lugar."}

        candidatos = candidatos or self.candidatos(texto)
        base["candidatos"] = [{**c, "nombre": self.catalogo[c["clase"]]["nombre_clase"]} for c in candidatos]
        if not self.usar_modelo:
            return {**base, "estado": "sin_resultado", "capa": "embeddings", "confianza": "baja",
                    "nota": "Hay candidatos, pero falta el modelo que elige."}

        e = self._elegir(texto, candidatos)
        validos = {c["clase"] for c in candidatos}
        clases = [c for c in dict.fromkeys(e["clases"]) if c in validos]  # un código fuera de la lista se descarta
        estado = e["estado"]
        if estado in ("resuelto", "grupo", "ambiguo") and not clases:
            estado = "sin_resultado"
        if estado in ("sin_resultado", "no_es_giro"):
            clases = []
        if estado == "resuelto" and len(clases) > 1:
            estado = "grupo"
        return {**base, "estado": estado, "clases": self._clases(clases), "capa": "modelo", "confianza": "media",
                "nota": e["nota"]}


if __name__ == "__main__":
    traductor = TraductorGiro()
    r = traductor.traducir(" ".join(sys.argv[1:]))
    traductor.guardar_cache()
    r["candidatos"] = r["candidatos"][:5]
    print(json.dumps(r, ensure_ascii=False, indent=1))

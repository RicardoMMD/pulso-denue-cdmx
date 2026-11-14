"""Validación del estado en tres niveles (R6, R8): estructura, referencias y coherencia.

  1. Estructura: campos y valores permitidos (los modelos de escena.py). Si falla, no se corren 2 y 3: sus
     mensajes sobre un estado mal formado confunden más de lo que ayudan.
  2. Referencias: los identificadores existen en la edición (archivo de referencias, sin base de datos).
  3. Coherencia: la combinación tiene sentido (reglas de la spec §4).

El dispositivo no es un nivel: en celular el motor sustituye puntos por el agregado que declara cada escena.
Cada error trae `nivel`, `ruta` (JSON Pointer), `codigo` estable y `mensaje` en español que nombra el campo y la razón.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from . import catalogo as cat
from .escena import Estado
from .referencias import Referencias
from .vista_exacta import vista_exacta


@dataclass(frozen=True)
class ErrorValidacion:
    nivel: int
    ruta: str
    codigo: str
    mensaje: str

    def a_dict(self) -> dict:
        return {"nivel": self.nivel, "ruta": self.ruta, "codigo": self.codigo, "mensaje": self.mensaje}


@dataclass(frozen=True)
class Contexto:
    """Dónde se escribió el estado. Hoy solo importa para los recorridos fijos (solo de historia)."""

    origen: str = "explorador"


class EstadoInvalido(Exception):
    def __init__(self, errores: list[ErrorValidacion]):
        self.errores = errores
        super().__init__("; ".join(f"{e.ruta or '/'}: {e.mensaje}" for e in errores))


# --- Nivel 1 -----------------------------------------------------------------------------------------------

_ETIQUETAS_UNION = {"ciudad_de_luz", "corredores_metro", "ciudades_dentro", "ajustar", "angulo", "recorrido"}
_CAMPOS_UNION = {"escena", "encuadre"}
_CAMPOS_TEXTO = {"titulo", "texto", "nota_cautela"}


def a_ruta(segmentos) -> str:
    return "".join("/" + str(s).replace("~", "~0").replace("/", "~1") for s in segmentos)


def _segmentos(loc: tuple) -> list:
    """Quita lo que Pydantic agrega a la ruta: la etiqueta de la unión y el nombre de clase de las uniones simples."""
    limpios = []
    for i, seg in enumerate(loc):
        if i > 0 and loc[i - 1] in _CAMPOS_UNION and seg in _ETIQUETAS_UNION:
            continue
        if isinstance(seg, str) and seg[:1].isupper():
            continue
        limpios.append(seg)
    return limpios


def _traducir(err: dict) -> tuple[str, str]:
    tipo, ctx = err["type"], err.get("ctx") or {}
    if tipo == "missing":
        return "campo_faltante", "falta el campo obligatorio"
    if tipo == "extra_forbidden":
        return "campo_no_admitido", "el campo no está permitido aquí"
    if tipo == "literal_error":
        return "valor_no_admitido", f"valor no admitido; se permite: {ctx.get('expected', '')}".rstrip("; ")
    if tipo == "union_tag_invalid":
        return "valor_no_admitido", f"valor no admitido; se permite: {ctx.get('expected_tags', '')}"
    if tipo == "union_tag_not_found":
        return "campo_faltante", f"falta el campo '{ctx.get('discriminator', '')}'"
    if tipo == "string_pattern_mismatch":
        if err["loc"][-1] in _CAMPOS_TEXTO:
            return ("texto_con_cifras",
                    "el texto no admite dígitos ni llaves fuera de los huecos {nombre}; las cifras se vinculan")
        return "formato_incorrecto", "no cumple el formato esperado"
    if tipo in ("string_too_long", "too_long"):
        return "demasiado_largo", f"excede el máximo permitido ({ctx.get('max_length')})"
    if tipo in ("string_too_short", "too_short"):
        return "demasiado_corto", f"es más corto que el mínimo permitido ({ctx.get('min_length')})"
    if tipo.endswith("_type") or tipo.endswith("_parsing"):
        return "tipo_incorrecto", "el tipo de dato no es el esperado"
    return "estructura_invalida", err["msg"]


def errores_estructura(exc: ValidationError) -> list[ErrorValidacion]:
    vistos, errores = set(), []
    for err in exc.errors():
        ruta = a_ruta(_segmentos(err["loc"]))
        codigo, razon = _traducir(err)
        if (ruta, codigo) in vistos:
            continue
        vistos.add((ruta, codigo))
        campo = ruta.rsplit("/", 1)[-1] or "el estado"
        errores.append(ErrorValidacion(1, ruta, codigo, f"{campo}: {razon}"))
    return sorted(errores, key=lambda e: (e.ruta, e.codigo))


def validar_estructura(datos: Any) -> tuple[Estado | None, list[ErrorValidacion]]:
    try:
        return Estado.model_validate(datos), []
    except ValidationError as exc:
        return None, errores_estructura(exc)


# --- Nivel 2 -----------------------------------------------------------------------------------------------

def _referencias(estado: Estado, ref: Referencias) -> list[ErrorValidacion]:
    errores: list[ErrorValidacion] = []
    if estado.edicion != ref.edicion:
        errores.append(ErrorValidacion(
            2, "/edicion", "edicion_no_disponible",
            f"edicion: la edición {estado.edicion} no está en las referencias (solo {ref.edicion})"))

    def territorio(t, ruta):
        if not ref.existe(t.tipo, t.clave):
            errores.append(ErrorValidacion(
                2, f"{ruta}/clave", "referencia_inexistente",
                f"clave: {t.tipo} '{t.clave}' no existe en la edición {ref.edicion}"))

    def seleccion(s, ruta):
        for i, codigo in enumerate(s.scian or []):
            if not ref.scian_valido(codigo):
                errores.append(ErrorValidacion(
                    2, f"{ruta}/scian/{i}", "scian_inexistente",
                    f"scian: el código {codigo} no existe en {ref.version_scian}"))

    territorio(estado.territorio, "/territorio")
    seleccion(estado.seleccion, "/seleccion")
    if estado.comparacion is not None:
        if hasattr(estado.comparacion, "territorio"):
            territorio(estado.comparacion.territorio, "/comparacion/territorio")
        else:
            seleccion(estado.comparacion.seleccion, "/comparacion/seleccion")
    if estado.escena.tipo == "ciudades_dentro":
        for i, t in enumerate(estado.escena.tipo_conglomerado or []):
            if not ref.tipo_conglomerado_valido(t):
                errores.append(ErrorValidacion(
                    2, f"/escena/tipo_conglomerado/{i}", "tipo_conglomerado_inexistente",
                    f"tipo_conglomerado: '{t}' no es un tipo de conglomerado de la edición {ref.edicion}"))
    return errores


# --- Nivel 3 -----------------------------------------------------------------------------------------------

_HUECO = re.compile(r"\{([a-z_]+)\}")


def _coherencia(estado: Estado, ref: Referencias, ctx: Contexto) -> list[ErrorValidacion]:
    errores: list[ErrorValidacion] = []

    def err(ruta, codigo, mensaje):
        errores.append(ErrorValidacion(3, ruta, codigo, mensaje))

    escena, territorio = estado.escena, estado.territorio
    permitidos = cat.ESCENAS[escena.tipo]["territorios"][escena.modo]
    if territorio.tipo not in permitidos:
        err("/territorio/tipo", "territorio_no_admitido",
            f"tipo: {escena.tipo} en modo {escena.modo} no admite territorio '{territorio.tipo}'; "
            f"admite: {', '.join(permitidos)}")

    def radio(t, ruta):
        if t.radio_m is None:
            return
        if escena.tipo == "corredores_metro":
            err(f"{ruta}/radio_m", "radio_no_admitido",
                "radio_m: en corredores_metro el radio es el de la escena; no se escribe en el territorio")
        elif t.tipo not in cat.TERRITORIOS_CON_RADIO:
            err(f"{ruta}/radio_m", "radio_no_admitido",
                f"radio_m: un territorio '{t.tipo}' no admite radio (solo {', '.join(cat.TERRITORIOS_CON_RADIO)})")

    radio(territorio, "/territorio")
    comp = estado.comparacion
    comp_territorio = getattr(comp, "territorio", None)
    comp_seleccion = getattr(comp, "seleccion", None)
    if comp_territorio is not None:
        radio(comp_territorio, "/comparacion/territorio")

    # Comparación
    if comp_territorio is not None:
        if (comp_territorio.tipo, comp_territorio.clave) == (territorio.tipo, territorio.clave):
            err("/comparacion", "comparacion_misma", "comparacion: se compara un territorio consigo mismo")
        pares = {territorio.tipo: territorio.clave, comp_territorio.tipo: comp_territorio.clave}
        if territorio.tipo != comp_territorio.tipo and set(pares) == {"estacion_metro", "linea_metro"}:
            if (ref.existe("estacion_metro", pares["estacion_metro"]) and ref.existe("linea_metro", pares["linea_metro"])
                    and not ref.linea_pasa_por(pares["linea_metro"], pares["estacion_metro"])):
                err("/comparacion/territorio", "estacion_fuera_de_linea",
                    f"territorio: la estación '{pares['estacion_metro']}' no está en la línea {pares['linea_metro']}")
    if comp_seleccion is not None and comp_seleccion == estado.seleccion:
        err("/comparacion", "comparacion_misma", "comparacion: se compara una selección consigo misma")

    # Recorrido
    enc = estado.encuadre
    if enc.modo == "recorrido":
        admitidos = cat.ESCENAS[escena.tipo]["recorridos"][escena.modo]
        if enc.recorrido not in admitidos:
            err("/encuadre/recorrido", "recorrido_no_admitido",
                f"recorrido: '{enc.recorrido}' no corresponde a {escena.tipo} en modo {escena.modo}")
        elif enc.recorrido in cat.RECORRIDOS_FIJOS and ctx.origen != "historia":
            err("/encuadre/recorrido", "recorrido_fijo_fuera_de_historia",
                f"recorrido: '{enc.recorrido}' es fijo y solo lo puede usar una historia")

    # Selección SCIAN: un código no puede contener a otro de la lista
    for lista, ruta in ((estado.seleccion.scian, "/seleccion/scian"),
                        (getattr(comp_seleccion, "scian", None), "/comparacion/seleccion/scian")):
        codigos = lista or []
        for i in range(len(codigos)):
            for j in range(i + 1, len(codigos)):
                a, b = codigos[i], codigos[j]
                if a.startswith(b) or b.startswith(a):
                    err(ruta, "scian_mezcla_niveles_redundantes",
                        f"scian: {a} y {b} se contienen; deja solo el código más general")

    if escena.tipo == "ciudades_dentro" and escena.tamano == "establecimientos_seleccion" and estado.seleccion.vacia():
        err("/escena/tamano", "tamano_sin_seleccion",
            "tamano: 'establecimientos_seleccion' exige una selección (por ejemplo, un giro SCIAN)")

    # Narrativa: cifras y huecos
    nar, vista = estado.narrativa, vista_exacta(estado)
    declarados = set(cat.HUECOS_RESERVADOS)
    if nar.principal is not None:
        declarados.add("principal")
        if nar.principal.medida not in vista.medidas:
            err("/narrativa/principal/medida", "cifra_no_disponible",
                f"medida: '{nar.principal.medida}' no existe en la vista exacta de este estado "
                f"({', '.join(vista.medidas)})")
    vistos: set[str] = set()
    for i, sec in enumerate(nar.secundarias):
        if sec.medida not in vista.medidas:
            err(f"/narrativa/secundarias/{i}/medida", "cifra_no_disponible",
                f"medida: '{sec.medida}' no existe en la vista exacta de este estado ({', '.join(vista.medidas)})")
        if sec.nombre in declarados or sec.nombre in vistos:
            err(f"/narrativa/secundarias/{i}/nombre", "hueco_duplicado",
                f"nombre: '{sec.nombre}' ya está en uso como hueco")
        vistos.add(sec.nombre)
    declarados |= vistos
    for campo in ("titulo", "texto", "nota_cautela"):
        for hueco in dict.fromkeys(_HUECO.findall(getattr(nar, campo))):
            if hueco not in declarados:
                err(f"/narrativa/{campo}", "hueco_sin_declarar",
                    f"{campo}: el hueco {{{hueco}}} no es una cifra declarada ni un hueco reservado")
    return errores


# --- Entrada -----------------------------------------------------------------------------------------------

def validar(estado: Estado | dict, referencias: Referencias, contexto: Contexto | None = None) -> list[ErrorValidacion]:
    """Devuelve los errores de los tres niveles, ordenados por nivel y ruta. Lista vacía = estado válido."""
    contexto = contexto or Contexto()
    if not isinstance(estado, Estado):
        estado, errores = validar_estructura(estado)
        if errores:
            return errores
    errores = _referencias(estado, referencias) + _coherencia(estado, referencias, contexto)
    return sorted(errores, key=lambda e: (e.nivel, e.ruta, e.codigo))


def nivel_del_veredicto(errores: list[ErrorValidacion]) -> int | None:
    return min((e.nivel for e in errores), default=None)

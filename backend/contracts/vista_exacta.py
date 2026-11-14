"""Vista exacta derivada del estado (R11).

La vista exacta no se guarda ni se escribe: es función del estado. Aquí solo se describe (tabla de `semantic`,
filtros, tipo de resultado y medidas disponibles). Ejecutar la consulta y congelar resultados es de H13 y H14.
Las cifras de la narrativa solo pueden nombrar medidas de esta vista (nivel 3: `cifra_no_disponible`).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import catalogo as cat
from .escena import Estado


@dataclass(frozen=True)
class VistaExacta:
    tipo_resultado: str  # ranking | territorial | comparacion | perfil | serie
    tablas: tuple[str, ...]
    medidas: tuple[str, ...]
    filtros: dict = field(default_factory=dict)


def vista_exacta(estado: Estado) -> VistaExacta:
    escena = estado.escena
    base = cat.VISTAS[(escena.tipo, escena.modo)]
    tablas = tuple(base.get("tablas", ()))
    medidas = list(base["medidas"])
    territorio = estado.territorio

    if escena.tipo == "ciudad_de_luz":
        # resumen_territorio y perfil_sector solo conocen ciudad, alcaldía y colonia.
        tablas = (("resumen_territorio", "perfil_sector") if territorio.tipo in cat.TERRITORIOS_CON_RESUMEN
                  else ("establecimiento",))
    elif escena.tipo == "corredores_metro" and escena.modo == "ranking" and territorio.tipo != "ciudad":
        # metro_estacion.lugar es el puesto en toda la ciudad; dentro de una línea el orden se recalcula.
        medidas.remove("lugar")
    elif escena.tipo == "ciudades_dentro" and escena.modo == "exterior" and not estado.seleccion.vacia():
        tablas += ("establecimiento",)
        medidas.insert(1, "establecimientos_seleccion")

    filtros: dict = {"edicion": estado.edicion, "territorio": territorio.model_dump(exclude_none=True),
                     "modo": escena.modo}
    if escena.tipo == "corredores_metro":
        filtros["radio_m"] = escena.radio_m
    elif escena.tipo == "ciudades_dentro" and escena.tipo_conglomerado is not None:
        filtros["tipo_conglomerado"] = list(escena.tipo_conglomerado)
    if not estado.seleccion.vacia():
        filtros["seleccion"] = estado.seleccion.model_dump(exclude_none=True)
    if estado.comparacion is not None:
        filtros["comparacion"] = estado.comparacion.model_dump(exclude_none=True)

    return VistaExacta(tipo_resultado=base["tipo_resultado"], tablas=tablas, medidas=tuple(medidas), filtros=filtros)

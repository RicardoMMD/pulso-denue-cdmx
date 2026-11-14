"""Carga y consulta del archivo de referencias (nivel 2 de la validación), sin base de datos."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DIRECTORIO = Path(__file__).resolve().parent / "referencias"


@dataclass(frozen=True)
class Referencias:
    edicion: str
    fecha_corte: str
    version_scian: str
    lugares: dict[str, dict[str, str]]
    lineas: dict[str, dict]
    scian: frozenset[str]
    tipos_conglomerado: frozenset[str]

    def existe(self, tipo: str, clave: str) -> bool:
        if tipo == "linea_metro":
            return clave in self.lineas
        return clave in self.lugares.get(tipo, {})

    def nombre(self, tipo: str, clave: str) -> str | None:
        if tipo == "linea_metro":
            linea = self.lineas.get(clave)
            return linea["nombre"] if linea else None
        return self.lugares.get(tipo, {}).get(clave)

    def linea_pasa_por(self, cve_linea: str, estacion: str) -> bool:
        linea = self.lineas.get(cve_linea)
        return bool(linea) and estacion in linea["estaciones"]

    def scian_valido(self, codigo: str) -> bool:
        return codigo in self.scian

    def tipo_conglomerado_valido(self, tipo: str) -> bool:
        return tipo in self.tipos_conglomerado


def desde_dict(d: dict) -> Referencias:
    return Referencias(
        edicion=d["edicion"], fecha_corte=d["fecha_corte"], version_scian=d["version_scian"],
        lugares=d["lugares"], lineas=d["lineas"], scian=frozenset(d["scian"]),
        tipos_conglomerado=frozenset(d["tipos_conglomerado"]))


def cargar(edicion_o_ruta: str | Path) -> Referencias:
    ruta = Path(edicion_o_ruta)
    if not ruta.suffix:
        ruta = DIRECTORIO / f"{edicion_o_ruta}.json"
    return desde_dict(json.loads(ruta.read_text(encoding="utf-8")))

"""Validación de historias (R13): `validar-historias` aplica la herencia panel por panel y valida cada panel.

Una historia es un archivo YAML en `contenido/historias/`:

    slug: vida-comercial-del-metro
    titulo: Vida comercial del Metro
    exploracion: bloqueada          # o libre; propiedad de la historia, no del estado
    paneles:
      - estado: {...}               # el primero es completo
      - estado: {territorio: {...}} # los demás son parciales y heredan del anterior
        exploracion: libre          # excepción por panel

Uso: `uv run python -m contracts.validar_historias [archivo_o_directorio ...]` (sin argumentos: contenido/historias).
Termina con código 1 si alguna historia no es válida. No necesita la base: usa el archivo de referencias.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .escena import Estado
from .herencia import heredar
from .referencias import Referencias, cargar
from .validar import Contexto, ErrorValidacion, EstadoInvalido, a_ruta, errores_estructura, validar, validar_estructura

RAIZ_REPO = Path(__file__).resolve().parents[2]
DIRECTORIO_HISTORIAS = RAIZ_REPO / "contenido" / "historias"


class Panel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # La pregunta que responde el panel: es del guion (H12), no del estado, así que no entra al id del panel.
    pregunta: Optional[str] = Field(default=None, min_length=1, max_length=160)
    estado: dict
    exploracion: Optional[Literal["bloqueada", "libre"]] = None


class Historia(BaseModel):
    model_config = ConfigDict(extra="forbid")
    slug: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    titulo: str = Field(min_length=1, max_length=120)
    exploracion: Literal["bloqueada", "libre"] = "bloqueada"
    paneles: list[Panel] = Field(min_length=1)


@dataclass(frozen=True)
class ErrorHistoria:
    archivo: str
    panel: int | None  # 1 = primero; None = la historia en general
    error: ErrorValidacion

    def __str__(self) -> str:
        donde = f"panel {self.panel}" if self.panel else "historia"
        return f"{self.archivo}: {donde}: {self.error.ruta or '/'} [{self.error.codigo}] {self.error.mensaje}"


def estados_de(historia: Historia) -> list[tuple[int, Estado | None, list[ErrorValidacion]]]:
    """Aplica la herencia: devuelve, por panel, el estado completo (si se pudo armar) y los errores de nivel 1."""
    resultado: list[tuple[int, Estado | None, list[ErrorValidacion]]] = []
    anterior: Estado | None = None
    for n, panel in enumerate(historia.paneles, start=1):
        if n == 1:
            estado, errores = validar_estructura(panel.estado)
        else:
            try:
                estado, errores = (heredar(anterior, panel.estado) if anterior else None), []
                if anterior is None:
                    errores = [ErrorValidacion(1, "", "panel_sin_base", "no hay un panel anterior válido del cual heredar")]
            except EstadoInvalido as exc:
                estado, errores = None, exc.errores
        resultado.append((n, estado, errores))
        anterior = estado if estado is not None else anterior
    return resultado


def validar_historia(datos: dict, ref: Referencias, archivo: str = "historia") -> list[ErrorHistoria]:
    try:
        historia = Historia.model_validate(datos)
    except ValidationError as exc:
        return [ErrorHistoria(archivo, None, e) for e in errores_estructura(exc)]
    errores: list[ErrorHistoria] = []
    for n, estado, de_estructura in estados_de(historia):
        errores += [ErrorHistoria(archivo, n, e) for e in de_estructura]
        if estado is not None:
            errores += [ErrorHistoria(archivo, n, e) for e in validar(estado, ref, Contexto(origen="historia"))]
    return errores


def validar_archivo(ruta: Path) -> list[ErrorHistoria]:
    try:
        datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [ErrorHistoria(ruta.name, None, ErrorValidacion(1, "", "yaml_invalido", f"no se pudo leer el YAML: {exc}"))]
    if not isinstance(datos, dict):
        return [ErrorHistoria(ruta.name, None, ErrorValidacion(1, "", "yaml_invalido", "la historia debe ser un mapa"))]
    edicion = (datos.get("paneles") or [{}])[0].get("estado", {}).get("edicion") if isinstance(datos.get("paneles"), list) else None
    try:
        ref = cargar(edicion or "2026-05")
    except FileNotFoundError:
        return [ErrorHistoria(ruta.name, 1, ErrorValidacion(
            2, "/edicion", "edicion_no_disponible", f"edicion: no hay archivo de referencias para {edicion}"))]
    return validar_historia(datos, ref, ruta.name)


def archivos(entradas: list[Path]) -> list[Path]:
    salida: list[Path] = []
    for e in entradas:
        salida += sorted(list(e.glob("*.yml")) + list(e.glob("*.yaml"))) if e.is_dir() else [e]
    return salida


def main(argv: list[str] | None = None) -> int:
    entradas = [Path(a) for a in (argv if argv is not None else sys.argv[1:])] or [DIRECTORIO_HISTORIAS]
    lista = archivos(entradas)
    if not lista:
        print("validar-historias: no hay historias que validar")
        return 0
    fallos = 0
    for ruta in lista:
        errores = validar_archivo(ruta)
        if errores:
            fallos += 1
            for e in errores:
                print(e, file=sys.stderr)
        else:
            print(f"ok  {ruta.name}")
    if fallos:
        print(f"validar-historias: {fallos} de {len(lista)} historias con errores", file=sys.stderr)
        return 1
    print(f"validar-historias: OK ({len(lista)} historias)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

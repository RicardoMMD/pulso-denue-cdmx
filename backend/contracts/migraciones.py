"""Migraciones entre versiones del contrato (R10).

Un cambio incompatible sube `catalogo.VERSION` y agrega aquí `migrar_vN_a_vN+1`, para que los paneles guardados
(H14) sigan abriendo. `migrar` lleva cualquier versión anterior a la vigente, paso por paso. No hay migraciones
reales todavía: v1 es la primera versión. La prueba usa una v2 ficticia para comprobar la maquinaria.
"""
from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy

from . import catalogo
from .escena import Estado
from .validar import ErrorValidacion, EstadoInvalido, validar_estructura

Migracion = Callable[[dict], dict]

# Clave = versión de origen. La función devuelve el estado en la versión siguiente (y con `contrato` actualizado).
REGISTRO: dict[int, Migracion] = {}


def migrar_datos(datos: dict, version_actual: int = catalogo.VERSION, registro: dict[int, Migracion] | None = None) -> dict:
    registro = REGISTRO if registro is None else registro
    datos = deepcopy(datos)
    version = datos.get("contrato")
    if not isinstance(version, int) or isinstance(version, bool):
        raise EstadoInvalido([ErrorValidacion(1, "/contrato", "campo_faltante", "contrato: falta la versión del contrato")])
    if version > version_actual:
        raise EstadoInvalido([ErrorValidacion(
            1, "/contrato", "version_futura",
            f"contrato: la versión {version} es posterior a la vigente ({version_actual})")])
    while version < version_actual:
        if version not in registro:
            raise EstadoInvalido([ErrorValidacion(
                1, "/contrato", "migracion_inexistente", f"contrato: no hay migración desde la versión {version}")])
        datos = registro[version](datos)
        if datos.get("contrato") != version + 1:
            raise RuntimeError(f"La migración desde v{version} debe dejar contrato = {version + 1}")
        version += 1
    return datos


def migrar(estado_json: dict) -> Estado:
    """Lleva un estado de cualquier versión anterior a la vigente y lo valida (nivel 1)."""
    estado, errores = validar_estructura(migrar_datos(estado_json))
    if errores:
        raise EstadoInvalido(errores)
    return estado

"""Herencia de estados parciales (R5): `heredar(anterior, parcial) -> Estado`.

Las seis reglas de la síntesis ("Reglas de herencia"):
  1. Campos de un bloque: se fusionan campo por campo; lo no mencionado se hereda.
  2. Listas (capas, secundarias, scian...): se reemplazan completas, nunca se mezclan.
  3. `null` explícito: borra el campo y vuelve al valor predeterminado.
  4. Cambio de tipo de escena: se reinician parámetros, modo y codificación a los de la nueva escena; se conservan
     territorio, selección y capas.
  5. Narrativa: se hereda como plantilla (se fusiona); sus cifras se vuelven a vincular con la vista exacta nueva.
  6. Vista exacta: se recalcula siempre (es función del estado; no se hereda porque no se guarda).

Dos precisiones que la spec hace sobre esas reglas, para que el resultado siga siendo un estado coherente:
  - El territorio se reemplaza completo cuando el parcial trae `tipo` o `clave` (otra referencia, otro radio); si solo
    trae `radio_m`, se fusiona. Heredar el radio de una estación a una alcaldía no tendría sentido. Si solo trae la
    `clave`, el `tipo` se hereda (otra alcaldía, otra estación); la clave y el radio nunca se heredan.
  - Al cambiar de escena el encuadre vuelve a `ajustar` salvo que el parcial lo traiga: un recorrido pertenece a una
    escena y un modo.
El resultado se valida como `Estado`; si no es válido se lanza `EstadoInvalido` con los mismos errores de nivel 1.
"""
from __future__ import annotations

from copy import deepcopy
from pydantic import ValidationError

from .escena import Estado, EstadoParcial
from .validar import ErrorValidacion, EstadoInvalido, errores_estructura


def _fusionar(base: dict, cambio: dict) -> dict:
    for clave, valor in cambio.items():
        if valor is None:
            base.pop(clave, None)  # regla 3: null borra y vuelve al predeterminado
        elif isinstance(valor, dict) and isinstance(base.get(clave), dict):
            base[clave] = _fusionar(base[clave], valor)
        else:
            base[clave] = deepcopy(valor)  # regla 2: listas y escalares se reemplazan
    return base


def _sin_nulos(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def _territorio(base: dict | None, cambio: dict) -> dict:
    if "tipo" in cambio or "clave" in cambio or base is None:
        nuevo = _sin_nulos(cambio)
        if base is not None and "tipo" not in nuevo and "clave" in nuevo:
            nuevo = {"tipo": base["tipo"], **nuevo}  # solo cambia la clave: misma clase de lugar, otra referencia
        return nuevo
    return _fusionar(deepcopy(base), cambio)


def _escena(base: dict, cambio: dict) -> tuple[dict, bool]:
    nuevo_tipo = cambio.get("tipo") or base["tipo"]
    if nuevo_tipo != base["tipo"]:  # regla 4
        return {"tipo": nuevo_tipo, **_sin_nulos({k: v for k, v in cambio.items() if k != "tipo"})}, True
    return _fusionar(deepcopy(base), cambio), False


def _encuadre(base: dict, cambio: dict) -> dict:
    if cambio.get("modo") not in (None, base.get("modo")):
        return _sin_nulos(cambio)  # otro modo de encuadre: los campos del anterior no aplican
    return _fusionar(deepcopy(base), cambio)


def _comparacion(base: dict | None, cambio: dict) -> dict:
    if base is None:
        return _sin_nulos(cambio)
    for alterna in ("territorio", "seleccion"):
        otra = "seleccion" if alterna == "territorio" else "territorio"
        if cambio.get(alterna) is not None and otra in base:
            # Cambia de qué se compara: territorio y selección no se mezclan, pero la forma se hereda.
            return {**_sin_nulos({k: v for k, v in base.items() if k not in ("territorio", "seleccion")}), **_sin_nulos(cambio)}
    resultado = deepcopy(base)
    for clave, valor in cambio.items():
        if clave == "territorio" and valor is not None:
            resultado["territorio"] = _territorio(resultado.get("territorio"), valor)
        else:
            resultado = _fusionar(resultado, {clave: valor})
    return resultado


def heredar_dict(anterior: Estado, parcial: EstadoParcial | dict) -> dict:
    if not isinstance(parcial, EstadoParcial):
        try:
            parcial = EstadoParcial.model_validate(parcial)
        except ValidationError as exc:
            raise EstadoInvalido(errores_estructura(exc)) from exc
    cambio = parcial.model_dump(mode="json", exclude_unset=True)
    estado = anterior.model_dump(mode="json")

    cambio_territorio = cambio.pop("territorio", None) if "territorio" in cambio else None
    if cambio_territorio is not None:
        estado["territorio"] = _territorio(estado.get("territorio"), cambio_territorio)
    elif "territorio" in parcial.model_fields_set:  # null explícito: sin territorio, el estado no es válido
        estado.pop("territorio", None)

    escena_cambio = cambio.pop("escena", None) if "escena" in cambio else None
    escena_cambio_de_tipo = False
    if escena_cambio is not None:
        estado["escena"], escena_cambio_de_tipo = _escena(estado["escena"], escena_cambio)
    elif "escena" in parcial.model_fields_set:
        estado.pop("escena", None)

    if "encuadre" in cambio:
        valor = cambio.pop("encuadre")
        if valor is None:
            estado.pop("encuadre", None)
        else:
            estado["encuadre"] = _encuadre(estado["encuadre"], valor)
    elif escena_cambio_de_tipo:
        estado.pop("encuadre", None)

    if "comparacion" in cambio:
        valor = cambio.pop("comparacion")
        if valor is None:
            estado.pop("comparacion", None)
        else:
            estado["comparacion"] = _comparacion(estado.get("comparacion"), valor)

    return _fusionar(estado, cambio)  # edición, selección, capas y narrativa: reglas generales


def heredar(anterior: Estado, parcial: EstadoParcial | dict) -> Estado:
    datos = heredar_dict(anterior, parcial)
    try:
        return Estado.model_validate(datos)
    except ValidationError as exc:
        raise EstadoInvalido(errores_estructura(exc)) from exc


__all__ = ["heredar", "heredar_dict", "EstadoInvalido", "ErrorValidacion"]

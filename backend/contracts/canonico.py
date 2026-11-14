"""Forma canónica del estado (R9): la base del id por contenido (SHA-256 → base62, H14).

JSON UTF-8 con claves ordenadas, sin campos que valgan su predeterminado, sin espacios y con textos en NFC.
`contracts-ts/canonico.ts` hace lo mismo en el navegador (la URL `#s=` del explorador) y el banco de bytes
esperados (`casos/canonico/`) comprueba que ambos produzcan exactamente los mismos bytes.

Reglas que mantienen la paridad:
  - Se omite todo valor igual a su predeterminado del esquema (null, [], el encuadre `ajustar`, radio 500...).
  - El estado no contiene números de punto flotante (una prueba recorre el esquema y falla si aparece un `number`).
  - Un cambio aquí cambia los ids: es un cambio de versión del contrato.
"""
from __future__ import annotations

import json
import unicodedata
from typing import Any

from .escena import Estado


def _nfc(valor: Any) -> Any:
    if isinstance(valor, str):
        return unicodedata.normalize("NFC", valor)
    if isinstance(valor, list):
        return [_nfc(v) for v in valor]
    if isinstance(valor, dict):
        return {k: _nfc(v) for k, v in valor.items()}
    return valor


def canonico_dict(estado: Estado) -> dict:
    return _nfc(estado.model_dump(mode="json", exclude_defaults=True))


def canonico(estado: Estado) -> bytes:
    return json.dumps(canonico_dict(estado), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

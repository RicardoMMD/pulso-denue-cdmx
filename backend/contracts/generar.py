"""Genera escena.v1.json desde los modelos y dispara la generación de los tipos TS y el validador Ajv (R1, R7).

Uso: `uv run python -m contracts.generar` (desde backend/). Es determinista: dos corridas seguidas no cambian nada.
Los archivos generados no se editan a mano; `make contratos` regenera y falla si el árbol cambia.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from . import catalogo
from .escena import esquema_estado

RAIZ = Path(__file__).resolve().parent
ESQUEMA = RAIZ / f"escena.v{catalogo.VERSION}.json"
TS = RAIZ.parent / "contracts-ts"


def ajustar_para_ajv(nodo):
    """Ajv no admite `discriminator.mapping`, y en modo estricto pide `type: object` junto al discriminador."""
    if isinstance(nodo, dict):
        if "discriminator" in nodo:
            nodo["discriminator"].pop("mapping", None)
            nodo.setdefault("type", "object")
        for valor in nodo.values():
            ajustar_para_ajv(valor)
    elif isinstance(nodo, list):
        for valor in nodo:
            ajustar_para_ajv(valor)
    return nodo


def esquema() -> dict:
    s = ajustar_para_ajv(esquema_estado())
    s["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    s["title"] = "Estado"
    return s


def escribir_esquema() -> None:
    ESQUEMA.write_text(json.dumps(esquema(), indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    escribir_esquema()
    print(f"escrito {ESQUEMA.relative_to(RAIZ.parent)}")
    if "--sin-ts" in sys.argv:
        return 0
    if not (TS / "node_modules").exists():
        print("Falta instalar Node: cd contracts-ts && npm ci", file=sys.stderr)
        return 1
    return subprocess.run(["node", "generar.mjs"], cwd=TS).returncode


if __name__ == "__main__":
    raise SystemExit(main())

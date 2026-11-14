import copy
import json
from pathlib import Path

import pytest

from contracts.referencias import cargar

RAIZ = Path(__file__).resolve().parents[2]
CASOS = RAIZ / "contracts" / "casos"

NARRATIVA = {"titulo": "Comercio en {territorio}", "texto": "Hay {principal} establecimientos.",
             "nota_cautela": "El DENUE no registra todo.", "principal": {"medida": "establecimientos"}}


def estado_base(**cambios) -> dict:
    base = {"contrato": 1, "edicion": "2026-05", "territorio": {"tipo": "ciudad", "clave": "09"},
            "escena": {"tipo": "ciudad_de_luz"}, "narrativa": copy.deepcopy(NARRATIVA)}
    base.update(cambios)
    return base


@pytest.fixture(scope="session")
def ref():
    return cargar("2026-05")


def casos(subdirectorio: str):
    return [pytest.param(json.loads(p.read_text(encoding="utf-8")), id=p.stem)
            for p in sorted((CASOS / subdirectorio).glob("*.json"))]

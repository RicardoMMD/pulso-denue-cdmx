"""R9: Python y TS producen bytes idénticos. Además del banco fijo, 300 estados aleatorios con texto difícil."""
import json
import random
import shutil
import subprocess
import unicodedata

import pytest

from contracts.canonico import canonico
from contracts.escena import Estado

from .conftest import RAIZ

TS = RAIZ / "contracts-ts"
pytestmark = pytest.mark.skipif(shutil.which("node") is None or not (TS / "node_modules").exists(),
                                reason="Node y contracts-ts/node_modules (npm ci) son necesarios")

LETRAS = "abcdefghijklmnopqrstuvwxyzáéíóúüñÑÁÉÍÓÚ ,.;:-_/\\\"'|()[]¿?¡!%&*+=<>~^`@#$ÅåØøßæ 🚇🏪✨\t\u001f  "
HUECOS = ["{territorio}", "{fecha_corte}", "{edicion}", "{principal}"]


def texto(rng: random.Random, largo: int) -> str:
    t = ""
    for _ in range(rng.randint(1, 8)):
        parte = rng.choice(HUECOS) if rng.random() < 0.15 else "".join(rng.choice(LETRAS) for _ in range(rng.randint(1, 6)))
        if len(t) + len(parte) > largo:
            break
        t += parte
    t = t or "x"
    if rng.random() < 0.4:  # el mismo texto descompuesto debe salir igual (NFC), si cabe en el límite
        descompuesto = unicodedata.normalize("NFD", t)
        t = descompuesto if len(descompuesto) <= largo else t
    return t


def estado_aleatorio(rng: random.Random) -> dict:
    tipo = rng.choice(["ciudad", "alcaldia", "colonia", "estacion_metro", "linea_metro", "conglomerado", "calle"])
    territorio = {"tipo": tipo, "clave": rng.choice(["09", "007", "002-001", "AGRICOLA ORIENTAL", "denue:CENTRAL DE ABASTO|PARQUE VIA VALLEJO|0", "002:1", "ESTACIÓN Ñ"])}
    if rng.random() < 0.3:
        territorio["radio_m"] = rng.choice([300, 500, 800])
    escena = rng.choice([
        {"tipo": "ciudad_de_luz"},
        {"tipo": "corredores_metro", **rng.choice([{}, {"modo": "ranking"}, {"radio_m": 800}, {"modo": "linea", "radio_m": 500}])},
        {"tipo": "ciudades_dentro", **rng.choice([{}, {"modo": "interior"}, {"tamano": "locales_declarados"},
                                                  {"tipo_conglomerado": ["mercado público", "tianguis, bazar o pulga"]}])},
    ])
    nar = {"titulo": texto(rng, 80), "texto": texto(rng, 400), "nota_cautela": texto(rng, 240)}
    if rng.random() < 0.7:
        nar["principal"] = {"medida": rng.choice(["establecimientos", "lugar", "nombre"]), **rng.choice(
            [{}, {"fila": "ultima"}, {"fila": {"clave": "ñ|:x"}}, {"formato": "texto"}, {"fila": "primera", "formato": "entero"}])}
    if rng.random() < 0.4:
        nar["secundarias"] = [{"nombre": rng.choice(["a", "b_c", "zeta"]) + "x" * i, "medida": "nombre", **rng.choice([{}, {"formato": "texto"}])} for i in range(rng.randint(0, 3))]
    estado = {"contrato": 1, "edicion": "2026-05", "territorio": territorio, "escena": escena, "narrativa": nar}
    if rng.random() < 0.3:
        estado["encuadre"] = rng.choice([{"modo": "ajustar"}, {"modo": "angulo", "angulo": "cenital"}, {"modo": "recorrido", "recorrido": "tren_de_luz"}])
    if rng.random() < 0.4:
        estado["seleccion"] = rng.choice([{}, {"scian": ["722", "46"]}, {"estrato": [3, 1], "tipo_unidad": "fijo"}, {"presencia_digital": False}, {"presencia_digital": None, "scian": None}])
    if rng.random() < 0.3:
        estado["capas"] = rng.sample(["alcaldias", "lineas_metro", "calles_principales", "etiquetas"], rng.randint(0, 4))
    if rng.random() < 0.3:
        estado["comparacion"] = rng.choice([{"forma": "lado_a_lado", "territorio": {"tipo": "alcaldia", "clave": "015"}},
                                            {"forma": "transformacion", "seleccion": {}}, {"forma": "transformacion", "seleccion": {"scian": ["31"]}}])
    return estado


def test_trescientos_estados_aleatorios_dan_los_mismos_bytes_en_python_y_ts():
    rng = random.Random(20261114)
    estados = [estado_aleatorio(rng) for _ in range(300)]
    esperados = [canonico(Estado.model_validate(e)).hex() for e in estados]  # también prueba que todos son válidos
    entrada = "\n".join(json.dumps(e, ensure_ascii=rng.random() < 0.5) for e in estados)
    salida = subprocess.run(["node", "canonico-lote.ts"], cwd=TS, input=entrada, capture_output=True, text=True, check=True)
    obtenidos = salida.stdout.split()
    assert len(obtenidos) == len(esperados)
    distintos = [i for i, (a, b) in enumerate(zip(obtenidos, esperados)) if a != b]
    assert not distintos, [(estados[i], bytes.fromhex(obtenidos[i]).decode(), bytes.fromhex(esperados[i]).decode()) for i in distintos[:2]]
    assert len(set(esperados)) > 250  # el generador produce variedad real

"""R1–R4: el modelo cierra lo que el principio "referencias, no datos" exige."""
import json

import pytest

from contracts import catalogo
from contracts.escena import Estado, EstadoParcial
from contracts.generar import ESQUEMA, esquema
from contracts.validar import validar_estructura

from .conftest import estado_base


def tipos_en(nodo):
    if isinstance(nodo, dict):
        if "type" in nodo:
            yield nodo["type"]
        for v in nodo.values():
            yield from tipos_en(v)
    elif isinstance(nodo, list):
        for v in nodo:
            yield from tipos_en(v)


def test_esquema_no_tiene_numeros_de_punto_flotante():
    """El estado no contiene floats: la forma canónica no puede diferir entre Python y JS por su formato."""
    assert "number" not in set(tipos_en(esquema()))


def test_json_schema_generado_esta_al_dia():
    esperado = json.dumps(esquema(), indent=1, ensure_ascii=False, sort_keys=True) + "\n"
    assert ESQUEMA.read_text(encoding="utf-8") == esperado, "Corre: uv run python -m contracts.generar"


def test_version_del_contrato_coincide_con_el_catalogo():
    assert catalogo.VERSION == 1
    assert esquema()["properties"]["contrato"]["const"] == catalogo.VERSION


def test_tres_escenas_de_la_primera_version():
    escenas = esquema()["properties"]["escena"]["oneOf"]
    assert len(escenas) == 3
    assert set(catalogo.ESCENAS) == {"ciudad_de_luz", "corredores_metro", "ciudades_dentro"}


@pytest.mark.parametrize("campo,valor", [
    ("color", "#ff0000"), ("escala", 3), ("coordenadas", [19.4, -99.1]), ("duracion_s", 1.2), ("puntos", [1, 2]),
    ("cifra", 1200), ("camara", {"x": 1}),
])
def test_no_hay_donde_escribir_cifras_colores_escalas_coordenadas_ni_tiempos(campo, valor):
    """R3: cada bloque rechaza campos que no declara."""
    for ruta in ("raiz", "territorio", "escena", "narrativa", "encuadre"):
        datos = estado_base()
        if ruta == "encuadre":
            datos["encuadre"] = {"modo": "ajustar"}
        destino = datos if ruta == "raiz" else datos.setdefault(ruta, {})
        destino[campo] = valor
        _, errores = validar_estructura(datos)
        assert any(e.codigo == "campo_no_admitido" for e in errores), (ruta, campo)


@pytest.mark.parametrize("texto", ["1,200 negocios", "mil 2 negocios", "Línea 12", "{principal} y 3", "llave { suelta", "llave } suelta"])
def test_textos_libres_sin_digitos_ni_llaves_fuera_de_huecos(texto):
    for campo in ("titulo", "texto", "nota_cautela"):
        datos = estado_base()
        datos["narrativa"][campo] = texto
        _, errores = validar_estructura(datos)
        assert any(e.codigo == "texto_con_cifras" and e.ruta == f"/narrativa/{campo}" for e in errores), (campo, texto)


def test_los_huecos_si_se_admiten():
    datos = estado_base()
    datos["narrativa"]["titulo"] = "{territorio} al {fecha_corte}"
    assert validar_estructura(datos)[1] == []


def test_los_numeros_en_texto_no_se_convierten_y_500_0_es_500():
    """Estricto: "500" no es un radio. 500.0 equivale a 500 (JSON de JS no los distingue) y se normaliza a entero."""
    assert validar_estructura(estado_base(escena={"tipo": "corredores_metro", "radio_m": "500"}))[1]
    estado, errores = validar_estructura(estado_base(escena={"tipo": "corredores_metro", "radio_m": 500.0}))
    assert errores == [] and type(estado.escena.radio_m) is int


def test_estado_parcial_todo_opcional_y_cerrado():
    EstadoParcial.model_validate({})
    EstadoParcial.model_validate({"territorio": None, "capas": None, "narrativa": {"principal": None}})
    with pytest.raises(Exception):
        EstadoParcial.model_validate({"color": "rojo"})
    with pytest.raises(Exception):
        EstadoParcial.model_validate({"escena": {"radio_m": 400}})


def test_modelo_estado_valida_un_estado_minimo():
    assert Estado.model_validate(estado_base()).escena.modo == "unico"

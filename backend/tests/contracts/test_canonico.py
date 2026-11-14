"""R9: forma canónica estable. Python y TS producen los mismos bytes (el banco lo comprueba en los dos lados)."""
import hashlib
import json

import pytest

from contracts.canonico import canonico
from contracts.escena import Estado
from contracts.validar import validar_estructura

from .conftest import casos, estado_base


@pytest.mark.parametrize("caso", casos("canonico"))
def test_bytes_esperados(caso):
    obtenido = canonico(Estado.model_validate(caso["estado"]))
    assert obtenido.hex() == caso["hex"]
    assert obtenido.decode("utf-8") == caso["texto"]


@pytest.mark.parametrize("caso", casos("canonico"))
def test_la_forma_canonica_vuelve_a_ser_un_estado_y_es_idempotente(caso):
    """La URL #s= lleva la forma canónica: tiene que poder abrirse otra vez y dar los mismos bytes."""
    de_vuelta, errores = validar_estructura(json.loads(caso["texto"]))
    assert errores == []
    assert canonico(de_vuelta) == caso["texto"].encode("utf-8")


def test_el_orden_de_las_claves_y_los_predeterminados_escritos_no_cambian_el_id():
    a = estado_base()
    b = dict(reversed(list(estado_base(encuadre={"modo": "ajustar"}, capas=[], seleccion={}, comparacion=None).items())))
    assert canonico(Estado.model_validate(a)) == canonico(Estado.model_validate(b))
    assert hashlib.sha256(canonico(Estado.model_validate(a))).digest() == hashlib.sha256(canonico(Estado.model_validate(b))).digest()


def test_un_cambio_real_si_cambia_el_id():
    a = canonico(Estado.model_validate(estado_base()))
    b = canonico(Estado.model_validate(estado_base(capas=["etiquetas"])))
    c = canonico(Estado.model_validate(estado_base(capas=["alcaldias"])))
    assert len({a, b, c}) == 3


def test_el_orden_de_las_listas_si_importa():
    a = canonico(Estado.model_validate(estado_base(capas=["alcaldias", "etiquetas"])))
    b = canonico(Estado.model_validate(estado_base(capas=["etiquetas", "alcaldias"])))
    assert a != b


def test_la_identidad_no_esta_en_el_estado():
    """Origen y panel anterior son metadatos: si estuvieran en el estado, el mismo panel tendría dos ids."""
    for campo in ("origen", "panel_anterior", "conversacion"):
        _, errores = validar_estructura(estado_base(**{campo: "x"}))
        assert [e.codigo for e in errores] == ["campo_no_admitido"], campo


def test_la_forma_canonica_es_utf8_compacta_y_sin_escapes_innecesarios():
    caso = canonico(Estado.model_validate(estado_base())).decode("utf-8")
    assert " " not in caso.replace("Hay {principal} establecimientos.", "").replace("Comercio en {territorio}", "").replace("El DENUE no registra todo.", "")
    assert "\\u" not in caso

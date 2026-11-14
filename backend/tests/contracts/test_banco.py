"""Banco compartido de veredictos (R7, R8): pytest corre los tres niveles; node --test corre el 1 y el 2."""
import pytest

from contracts.validar import Contexto, nivel_del_veredicto, validar

from .conftest import casos


@pytest.mark.parametrize("caso", casos("veredicto"))
def test_veredicto(caso, ref):
    errores = validar(caso["estado"], ref, Contexto(**caso.get("contexto", {})))
    resumen = [(e.nivel, e.codigo, e.ruta) for e in errores]
    assert (len(errores) == 0) == caso["valido"], resumen
    assert nivel_del_veredicto(errores) == caso["nivel"], resumen
    if not caso["valido"]:
        assert caso["codigo"] in [e.codigo for e in errores], resumen
        for e in errores:  # R6: los mensajes nombran el campo y la razón, en español
            assert e.mensaje and e.ruta.startswith("/") or e.ruta == ""
            assert e.codigo.replace("_", "").isalpha() and e.codigo.islower()


def test_cada_codigo_de_la_spec_tiene_un_caso():
    esperados = {
        "territorio_no_admitido", "radio_no_admitido", "estacion_fuera_de_linea", "recorrido_no_admitido",
        "recorrido_fijo_fuera_de_historia", "scian_mezcla_niveles_redundantes", "cifra_no_disponible",
        "hueco_sin_declarar", "comparacion_misma", "tamano_sin_seleccion", "hueco_duplicado",
        "referencia_inexistente", "scian_inexistente", "edicion_no_disponible", "tipo_conglomerado_inexistente",
        "campo_no_admitido", "campo_faltante", "valor_no_admitido", "texto_con_cifras", "formato_incorrecto",
        "demasiado_largo", "demasiado_corto",
    }
    cubiertos = {c.values[0]["codigo"] for c in casos("veredicto") if c.values[0]["codigo"]}
    assert esperados <= cubiertos, esperados - cubiertos


def test_nivel_1_detiene_los_demas(ref):
    """Un estado mal formado solo reporta nivel 1."""
    caso = {"contrato": 1, "edicion": "2031-05", "territorio": {"tipo": "ciudad", "clave": "XX"},
            "escena": {"tipo": "rarezas"}, "narrativa": {}}
    assert {e.nivel for e in validar(caso, ref)} == {1}

"""R11: la vista exacta se deriva del estado; las medidas disponibles dependen de la escena, el modo y el territorio."""
import pytest

from contracts.escena import Estado
from contracts.vista_exacta import vista_exacta

from .conftest import estado_base


def vista(**cambios):
    return vista_exacta(Estado.model_validate(estado_base(**cambios)))


def test_ciudad_de_luz_usa_resumen_solo_para_ciudad_alcaldia_y_colonia():
    assert vista().tablas == ("resumen_territorio", "perfil_sector") and vista().tipo_resultado == "territorial"
    assert vista(territorio={"tipo": "estacion_metro", "clave": "X"}).tablas == ("establecimiento",)


def test_corredores_linea_es_una_serie_y_ranking_un_ranking():
    linea = vista(territorio={"tipo": "linea_metro", "clave": "2"}, escena={"tipo": "corredores_metro"})
    # Las filas (estaciones) salen de metro_estacion; el total de la línea, de metro_linea (unión de radios).
    assert linea.tipo_resultado == "serie" and linea.tablas == ("metro_linea", "metro_recorrido", "metro_estacion")
    assert linea.filtros["radio_m"] == 500
    ranking = vista(escena={"tipo": "corredores_metro", "modo": "ranking", "radio_m": 800})
    assert ranking.tipo_resultado == "ranking" and ranking.tablas == ("metro_estacion",) and ranking.filtros["radio_m"] == 800


def test_lugar_solo_existe_con_territorio_ciudad():
    assert "lugar" in vista(escena={"tipo": "corredores_metro", "modo": "ranking"}).medidas
    dentro_de_linea = vista(territorio={"tipo": "linea_metro", "clave": "2"}, escena={"tipo": "corredores_metro", "modo": "ranking"})
    assert "lugar" not in dentro_de_linea.medidas


def test_ciudades_dentro_agrega_la_cifra_por_seleccion_solo_si_hay_seleccion():
    sin = vista(territorio={"tipo": "alcaldia", "clave": "007"}, escena={"tipo": "ciudades_dentro"})
    con = vista(territorio={"tipo": "alcaldia", "clave": "007"}, escena={"tipo": "ciudades_dentro"}, seleccion={"scian": ["722"]})
    assert "establecimientos_seleccion" not in sin.medidas and "establecimientos_seleccion" in con.medidas
    assert sin.tablas == ("conglomerado",) and con.tablas == ("conglomerado", "establecimiento")


def test_interior_es_un_perfil_del_conglomerado():
    v = vista(territorio={"tipo": "conglomerado", "clave": "x"}, escena={"tipo": "ciudades_dentro", "modo": "interior"})
    assert v.tipo_resultado == "perfil" and v.tablas == ("establecimiento",)


def test_la_corredores_no_ofrece_cifra_por_seleccion():
    v = vista(escena={"tipo": "corredores_metro"}, seleccion={"scian": ["722"]})
    assert "establecimientos_seleccion" not in v.medidas
    assert v.filtros["seleccion"] == {"scian": ["722"]}


def test_los_filtros_describen_el_estado_sin_valores_nulos():
    v = vista(comparacion={"forma": "lado_a_lado", "territorio": {"tipo": "alcaldia", "clave": "015"}})
    assert v.filtros["edicion"] == "2026-05" and v.filtros["territorio"] == {"tipo": "ciudad", "clave": "09"}
    assert v.filtros["comparacion"]["territorio"]["clave"] == "015"
    assert "None" not in str(v.filtros)


@pytest.mark.parametrize("escena,modo", [("ciudad_de_luz", "unico"), ("corredores_metro", "linea"), ("corredores_metro", "ranking"),
                                         ("ciudades_dentro", "exterior"), ("ciudades_dentro", "interior")])
def test_toda_combinacion_de_escena_y_modo_tiene_vista(escena, modo):
    from contracts import catalogo
    assert (escena, modo) in catalogo.VISTAS


def test_cada_medida_de_cada_vista_esta_definida_y_en_el_vocabulario():
    from typing import get_args

    from contracts import catalogo
    from contracts.escena import Medida
    for clave, base in catalogo.VISTAS.items():
        assert base["filas"], clave
        for medida, d in base["medidas"].items():
            assert medida in catalogo.MEDIDAS and medida in get_args(Medida), (clave, medida)
            assert d["definicion"] and isinstance(d["total"], bool), (clave, medida)
    assert set(catalogo.MEDIDAS) == set(get_args(Medida))


def test_la_vista_lleva_definiciones_solo_de_sus_medidas():
    v = vista(territorio={"tipo": "linea_metro", "clave": "2"}, escena={"tipo": "corredores_metro", "modo": "ranking"})
    assert set(v.definiciones) == set(v.medidas) and "lugar" not in v.definiciones
    con = vista(territorio={"tipo": "alcaldia", "clave": "007"}, escena={"tipo": "ciudades_dentro"}, seleccion={"scian": ["722"]})
    assert con.admite_total("establecimientos_seleccion")
    assert not vista().admite_total("participacion")

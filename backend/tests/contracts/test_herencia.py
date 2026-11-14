"""R5: cada una de las seis reglas de herencia tiene al menos una prueba, más el ejemplo de la síntesis."""
import pytest

from contracts.canonico import canonico
from contracts.escena import Estado
from contracts.herencia import EstadoInvalido, heredar
from contracts.validar import validar
from contracts.vista_exacta import vista_exacta

from .conftest import NARRATIVA, estado_base


@pytest.fixture
def mercados():
    """El primer panel del ejemplo de la síntesis: mercados de Iztapalapa con más locales de comida."""
    return Estado.model_validate(estado_base(
        territorio={"tipo": "alcaldia", "clave": "007"},
        escena={"tipo": "ciudades_dentro", "tamano": "establecimientos_seleccion", "tipo_conglomerado": ["mercado público"]},
        seleccion={"scian": ["722"], "estrato": [1, 2]},
        capas=["alcaldias", "etiquetas"],
        narrativa={"titulo": "Mercados de {territorio} con más comida", "texto": "{lider} concentra {principal}.",
                   "nota_cautela": "Cada local cuenta como un establecimiento.",
                   "principal": {"medida": "establecimientos_seleccion", "formato": "entero"},
                   "secundarias": [{"nombre": "lider", "medida": "nombre", "formato": "texto"}]}))


def test_ejemplo_de_la_sintesis_y_en_cuauhtemoc(mercados, ref):
    segundo = heredar(mercados, {"territorio": {"tipo": "alcaldia", "clave": "015"}})
    assert segundo.territorio.clave == "015"
    assert segundo.escena == mercados.escena and segundo.seleccion == mercados.seleccion
    assert segundo.narrativa == mercados.narrativa  # regla 5: la narrativa se hereda como plantilla
    assert validar(segundo, ref) == []


def test_regla_1_los_campos_de_un_bloque_se_fusionan(mercados):
    nuevo = heredar(mercados, {"seleccion": {"tipo_unidad": "fijo"}})
    assert nuevo.seleccion.scian == ["722"] and nuevo.seleccion.estrato == [1, 2] and nuevo.seleccion.tipo_unidad == "fijo"
    nuevo = heredar(mercados, {"escena": {"tamano": "locales_declarados"}})
    assert nuevo.escena.tipo_conglomerado == ["mercado público"] and nuevo.escena.tamano == "locales_declarados"
    nuevo = heredar(mercados, {"narrativa": {"principal": {"formato": "porcentaje"}}})
    assert nuevo.narrativa.principal.medida == "establecimientos_seleccion" and nuevo.narrativa.principal.formato == "porcentaje"


def test_regla_2_las_listas_se_reemplazan_nunca_se_mezclan(mercados):
    nuevo = heredar(mercados, {"capas": ["lineas_metro"], "seleccion": {"scian": ["461"]},
                               "narrativa": {"secundarias": [{"nombre": "otro", "medida": "tipo"}]}})
    assert nuevo.capas == ["lineas_metro"]
    assert nuevo.seleccion.scian == ["461"] and nuevo.seleccion.estrato == [1, 2]
    assert [s.nombre for s in nuevo.narrativa.secundarias] == ["otro"]


def test_regla_3_null_borra_el_campo_y_vuelve_al_predeterminado(mercados):
    nuevo = heredar(mercados, {"seleccion": {"scian": None}, "escena": {"tamano": None, "tipo_conglomerado": None},
                               "narrativa": {"principal": None}, "capas": None})
    assert nuevo.seleccion.scian is None and nuevo.seleccion.estrato == [1, 2]
    assert nuevo.escena.tamano == "establecimientos" and nuevo.escena.tipo_conglomerado is None
    assert nuevo.narrativa.principal is None and nuevo.capas == []
    assert heredar(mercados, {"seleccion": None}).seleccion.vacia()
    con_comparacion = heredar(mercados, {"comparacion": {"forma": "lado_a_lado", "territorio": {"tipo": "alcaldia", "clave": "015"}}})
    assert con_comparacion.comparacion is not None
    assert heredar(con_comparacion, {"comparacion": None}).comparacion is None


def test_regla_4_cambio_de_escena_reinicia_parametros_y_conserva_territorio_seleccion_y_capas(mercados):
    nuevo = heredar(mercados, {"escena": {"tipo": "corredores_metro"}})
    assert nuevo.escena.tipo == "corredores_metro" and nuevo.escena.modo == "linea" and nuevo.escena.radio_m == 500
    assert nuevo.territorio == mercados.territorio
    assert nuevo.seleccion == mercados.seleccion and nuevo.capas == mercados.capas
    # y el encuadre vuelve a ajustar, porque un recorrido pertenece a una escena y un modo
    con_recorrido = heredar(mercados, {"escena": {"modo": "interior"}, "encuadre": {"modo": "recorrido", "recorrido": "entrar_al_mercado"}})
    assert heredar(con_recorrido, {"escena": {"tipo": "ciudad_de_luz"}}).encuadre.modo == "ajustar"


def test_regla_4_un_parametro_de_otra_escena_no_pasa(mercados):
    with pytest.raises(EstadoInvalido) as exc:
        heredar(mercados, {"escena": {"tipo": "ciudad_de_luz", "radio_m": 300}})
    assert exc.value.errores[0].codigo == "campo_no_admitido" and exc.value.errores[0].ruta == "/escena/radio_m"


def test_regla_5_la_narrativa_es_plantilla_y_las_cifras_se_revinculan(mercados, ref):
    """Al cambiar de escena, la narrativa sigue ahí; sus cifras ya no existen y el nivel 3 lo dice (cifra_no_disponible)."""
    nuevo = heredar(mercados, {"escena": {"tipo": "corredores_metro"}, "territorio": {"tipo": "linea_metro", "clave": "2"}})
    assert nuevo.narrativa == mercados.narrativa
    assert {e.codigo for e in validar(nuevo, ref)} == {"cifra_no_disponible"}


def test_regla_6_la_vista_exacta_se_recalcula_siempre(mercados):
    antes = vista_exacta(mercados)
    despues = vista_exacta(heredar(mercados, {"escena": {"modo": "interior"}, "territorio": {"tipo": "conglomerado", "clave": "x"}}))
    assert antes.tipo_resultado == "ranking" and despues.tipo_resultado == "perfil"
    assert "vista_exacta" not in Estado.model_fields  # no se guarda en el estado: es función de él


def test_territorio_se_reemplaza_completo_si_cambia_la_referencia(mercados):
    con_radio = heredar(mercados, {"territorio": {"tipo": "conglomerado", "clave": "denue:X|Y|1", "radio_m": 300}})
    assert heredar(con_radio, {"territorio": {"radio_m": 500}}).territorio.radio_m == 500  # solo radio: se fusiona
    nuevo = heredar(con_radio, {"territorio": {"tipo": "alcaldia", "clave": "015"}})
    assert nuevo.territorio.radio_m is None  # otra referencia: no hereda el radio


def test_encuadre_de_otro_modo_no_arrastra_campos_del_anterior(mercados):
    angulo = heredar(mercados, {"encuadre": {"modo": "angulo", "angulo": "cenital"}})
    recorrido = heredar(angulo, {"encuadre": {"modo": "recorrido", "recorrido": "entrar_al_mercado"}})
    assert recorrido.encuadre.modo == "recorrido" and not hasattr(recorrido.encuadre, "angulo")


def test_comparacion_cambia_de_lo_que_compara_sin_mezclar(mercados):
    a = heredar(mercados, {"comparacion": {"forma": "lado_a_lado", "territorio": {"tipo": "alcaldia", "clave": "015"}}})
    b = heredar(a, {"comparacion": {"seleccion": {"scian": ["46"]}}})
    assert getattr(b.comparacion, "territorio", None) is None and b.comparacion.seleccion.scian == ["46"]
    c = heredar(a, {"comparacion": {"territorio": {"clave": "003"}}})
    assert c.comparacion.territorio.clave == "003"


def test_un_parcial_invalido_da_los_mismos_errores_de_nivel_1(mercados):
    with pytest.raises(EstadoInvalido) as exc:
        heredar(mercados, {"escena": {"radio_m": 400}})
    assert exc.value.errores[0].nivel == 1 and exc.value.errores[0].ruta == "/escena/radio_m"
    with pytest.raises(EstadoInvalido):
        heredar(mercados, {"territorio": None})
    with pytest.raises(EstadoInvalido):
        heredar(mercados, {"color": "rojo"})


def test_heredar_no_modifica_el_estado_anterior_y_es_determinista(mercados):
    antes = canonico(mercados)
    a = heredar(mercados, {"territorio": {"tipo": "alcaldia", "clave": "015"}, "capas": None})
    b = heredar(mercados, {"capas": None, "territorio": {"clave": "015", "tipo": "alcaldia"}})
    assert canonico(mercados) == antes and canonico(a) == canonico(b)


def test_el_estado_sin_parcial_se_hereda_igual(mercados):
    assert canonico(heredar(mercados, {})) == canonico(mercados)
    assert NARRATIVA["titulo"]  # (la fixture de estado_base no se usa aquí; evita un import sin uso)

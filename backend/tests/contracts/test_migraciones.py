"""R10: un estado v1 pasa por una migración a una v2 ficticia y sigue siendo válido."""
import pytest

from contracts.migraciones import migrar, migrar_datos
from contracts.escena import Estado
from contracts.validar import EstadoInvalido, validar_estructura

from .conftest import estado_base


def v1_a_v2(datos: dict) -> dict:
    """v2 ficticia: `edicion` pasa a llamarse `corte` y el contrato sube a 2."""
    nuevo = {k: v for k, v in datos.items() if k != "edicion"}
    nuevo["corte"] = datos["edicion"]
    nuevo["contrato"] = 2
    return nuevo


def v2_a_v3(datos: dict) -> dict:
    nuevo = dict(datos)
    nuevo["contrato"] = 3
    return nuevo


def test_el_estado_vigente_migra_a_si_mismo():
    estado = migrar(estado_base())
    assert isinstance(estado, Estado) and estado.contrato == 1


def test_v1_pasa_por_una_v2_ficticia_y_sigue_siendo_valido():
    """Se simula el futuro: la vigente es la 2 y su validación entiende `corte` en lugar de `edicion`."""
    v2 = migrar_datos(estado_base(), version_actual=2, registro={1: v1_a_v2})
    assert v2["contrato"] == 2 and v2["corte"] == "2026-05" and "edicion" not in v2
    # El contenido sigue siendo el mismo estado: deshaciendo el cambio de nombre vuelve a ser un v1 válido.
    de_vuelta = {**{k: v for k, v in v2.items() if k != "corte"}, "edicion": v2["corte"], "contrato": 1}
    assert validar_estructura(de_vuelta)[1] == []


def test_las_migraciones_se_encadenan_version_por_version():
    v3 = migrar_datos(estado_base(), version_actual=3, registro={1: v1_a_v2, 2: v2_a_v3})
    assert v3["contrato"] == 3 and v3["corte"] == "2026-05"


def test_no_modifica_el_original():
    original = estado_base()
    migrar_datos(original, version_actual=2, registro={1: v1_a_v2})
    assert original["contrato"] == 1 and "edicion" in original


def test_falta_la_migracion():
    with pytest.raises(EstadoInvalido) as exc:
        migrar_datos(estado_base(), version_actual=2, registro={})
    assert exc.value.errores[0].codigo == "migracion_inexistente"


def test_version_futura_o_ausente():
    with pytest.raises(EstadoInvalido) as exc:
        migrar(estado_base(contrato=9))
    assert exc.value.errores[0].codigo == "version_futura"
    sin = estado_base()
    del sin["contrato"]
    with pytest.raises(EstadoInvalido):
        migrar(sin)


def test_una_migracion_que_no_sube_la_version_es_un_error_de_programacion():
    with pytest.raises(RuntimeError):
        migrar_datos(estado_base(), version_actual=2, registro={1: lambda d: d})

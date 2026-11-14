"""R13: las historias válidas pasan y cada historia inválida falla con el código que su nombre anuncia."""
from pathlib import Path

import pytest

from contracts.validar_historias import DIRECTORIO_HISTORIAS, archivos, main, validar_archivo

INVALIDAS = Path(__file__).parent / "historias_invalidas"


def test_las_historias_del_repositorio_son_validas():
    lista = archivos([DIRECTORIO_HISTORIAS])
    assert lista, "tiene que haber al menos una historia de ejemplo"
    for ruta in lista:
        assert validar_archivo(ruta) == [], ruta.name


@pytest.mark.parametrize("ruta", sorted(INVALIDAS.glob("*.yml")), ids=lambda r: r.stem)
def test_historia_invalida_falla_con_su_codigo(ruta):
    codigo = ruta.stem.split("__")[0]
    errores = validar_archivo(ruta)
    assert codigo in [e.error.codigo for e in errores], [str(e) for e in errores]
    assert all(e.archivo == ruta.name for e in errores)


def test_el_ejemplo_hereda_el_segundo_panel_del_primero():
    from contracts.validar_historias import Historia, estados_de
    import yaml
    historia = Historia.model_validate(yaml.safe_load((DIRECTORIO_HISTORIAS / "ejemplo-mercados.yml").read_text(encoding="utf-8")))
    (_, uno, e1), (_, dos, e2) = estados_de(historia)
    assert e1 == [] and e2 == [] and uno.territorio.clave == "007" and dos.territorio.clave == "015"
    assert dos.narrativa == uno.narrativa and dos.escena == uno.escena


def test_el_comando_sale_en_0_con_historias_validas_y_en_1_con_una_invalida(capsys):
    assert main([str(DIRECTORIO_HISTORIAS)]) == 0
    assert main([str(INVALIDAS)]) == 1
    salida = capsys.readouterr()
    assert "texto_con_cifras" in salida.err and "panel 1" in salida.err


def test_yaml_roto_o_que_no_es_un_mapa(tmp_path, capsys):
    (tmp_path / "roto.yml").write_text("slug: [sin cerrar", encoding="utf-8")
    (tmp_path / "lista.yml").write_text("- a\n- b\n", encoding="utf-8")
    assert main([str(tmp_path)]) == 1
    assert capsys.readouterr().err.count("yaml_invalido") == 2


def test_directorio_sin_historias_no_falla(tmp_path):
    assert main([str(tmp_path)]) == 0

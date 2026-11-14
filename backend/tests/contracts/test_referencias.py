"""R12: el archivo de referencias versionado es consultable sin base de datos."""
import json

from contracts import referencias as mod
from contracts.exportar_referencias import codigos_scian


def test_archivo_de_la_edicion_vigente(ref):
    assert ref.edicion == "2026-05" and ref.version_scian == "SCIAN 2023" and ref.fecha_corte == "2026-05-20"
    assert len(ref.lineas) == 12 and {"1", "9", "12", "A", "B"} <= set(ref.lineas)
    assert ref.nombre("ciudad", "09") == "Ciudad de México" and ref.nombre("linea_metro", "A") == "Línea A"
    assert ref.existe("alcaldia", "007") and not ref.existe("alcaldia", "999") and not ref.existe("lugar_raro", "x")


def test_scian_va_de_sector_a_clase():
    assert all(c in __import__("contracts.referencias", fromlist=["x"]).cargar("2026-05").scian for c in ("31", "32", "33", "311", "3111"))
    assert not mod.cargar("2026-05").scian_valido("3")


def test_codigos_scian_son_los_prefijos_de_las_clases():
    assert codigos_scian(["311111", "311112"]) == ["31", "311", "3111", "31111", "311111", "311112"]


def test_el_archivo_es_chico_y_no_lleva_coordenadas():
    ruta = mod.DIRECTORIO / "2026-05.json"
    assert ruta.stat().st_size < 1_000_000
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert set(datos) == {"edicion", "fecha_corte", "lugares", "lineas", "scian", "tipos_conglomerado", "version_scian"}
    assert "latitud" not in ruta.read_text(encoding="utf-8")[:2000]


def test_linea_pasa_por(ref):
    assert ref.linea_pasa_por("A", "AGRICOLA ORIENTAL") and not ref.linea_pasa_por("2", "AGRICOLA ORIENTAL")
    assert not ref.linea_pasa_por("99", "AGRICOLA ORIENTAL")

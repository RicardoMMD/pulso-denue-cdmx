"""Catálogo de valores del contrato de escena v1.

Es la única lista de lo que cada escena admite: modos, predeterminados, territorios, recorridos, agregado en
celular y medidas de la vista exacta. `validar`, `herencia` y `vista_exacta` leen de aquí; nada de esto se repite.
Si cambia algo incompatible, sube `VERSION` y se escribe una migración (ver migraciones.py).
"""
from __future__ import annotations

VERSION = 1

TIPOS_TERRITORIO = ("ciudad", "alcaldia", "colonia", "estacion_metro", "linea_metro", "conglomerado", "calle")
TERRITORIOS_CON_RADIO = ("estacion_metro", "conglomerado")
RADIOS_M = (300, 500, 800)
ANGULOS = ("cenital", "oblicua", "rasante")
RECORRIDOS = ("el_despertar", "tren_de_luz", "constelacion_estaciones", "entrar_al_mercado")
CAPAS = ("alcaldias", "lineas_metro", "calles_principales", "etiquetas")
TIPOS_UNIDAD = ("fijo", "semifijo")
FORMAS_COMPARACION = ("lado_a_lado", "transformacion")
FORMATOS_CIFRA = ("entero", "porcentaje", "decimal1", "texto")
FILAS = ("primera", "ultima", "total")
ORIGENES = ("historia", "explorador", "analista")

# Medidas que una cifra de la narrativa puede nombrar (vocabulario cerrado). Cuáles existen en un estado
# concreto lo decide la vista exacta.
MEDIDAS = (
    "establecimientos", "establecimientos_seleccion", "locales_declarados", "estaciones", "estacion",
    "giro_dominante", "lugar", "macrosector", "participacion", "nombre", "tipo",
)

# Huecos que llena el motor y no hay que declarar.
HUECOS_RESERVADOS = ("territorio", "fecha_corte", "edicion")

ESCENAS: dict[str, dict] = {
    "ciudad_de_luz": {
        "modos": ("unico",),
        "modo_predeterminado": "unico",
        "territorios": {"unico": TIPOS_TERRITORIO},
        "agregado_celular": "ageb",
        "recorridos": {"unico": ("el_despertar",)},
    },
    "corredores_metro": {
        "modos": ("linea", "ranking"),
        "modo_predeterminado": "linea",
        "territorios": {
            "linea": ("linea_metro", "estacion_metro"),
            "ranking": ("ciudad", "linea_metro", "estacion_metro"),
        },
        "radio_predeterminado": 500,
        "agregado_celular": "estacion",
        "recorridos": {"linea": ("tren_de_luz",), "ranking": ("constelacion_estaciones",)},
    },
    "ciudades_dentro": {
        "modos": ("exterior", "interior"),
        "modo_predeterminado": "exterior",
        "territorios": {
            "exterior": ("ciudad", "alcaldia", "conglomerado"),
            "interior": ("conglomerado",),
        },
        "tamanos": ("establecimientos", "establecimientos_seleccion", "locales_declarados"),
        "tamano_predeterminado": "establecimientos",
        "agregado_celular": "conglomerado",
        "recorridos": {"exterior": (), "interior": ("entrar_al_mercado",)},
    },
}

# Recorridos que solo puede usar una historia (los demás son plantillas).
RECORRIDOS_FIJOS = ("el_despertar",)

# Medidas disponibles por escena y modo en la vista exacta (descripción declarativa; H13 y H14 ejecutan la consulta).
VISTAS: dict[tuple[str, str], dict] = {
    ("ciudad_de_luz", "unico"): {
        "tipo_resultado": "territorial",
        "medidas": ("establecimientos", "macrosector", "participacion"),
    },
    ("corredores_metro", "linea"): {
        "tipo_resultado": "serie",
        "tablas": ("metro_linea", "metro_recorrido"),
        "medidas": ("establecimientos", "estaciones", "estacion", "giro_dominante"),
    },
    ("corredores_metro", "ranking"): {
        "tipo_resultado": "ranking",
        "tablas": ("metro_estacion",),
        "medidas": ("establecimientos", "lugar", "estacion", "giro_dominante"),
    },
    ("ciudades_dentro", "exterior"): {
        "tipo_resultado": "ranking",
        "tablas": ("conglomerado",),
        "medidas": ("establecimientos", "locales_declarados", "nombre", "tipo"),
    },
    ("ciudades_dentro", "interior"): {
        "tipo_resultado": "perfil",
        "tablas": ("establecimiento",),
        "medidas": ("establecimientos", "nombre"),
    },
}
TERRITORIOS_CON_RESUMEN = ("ciudad", "alcaldia", "colonia")

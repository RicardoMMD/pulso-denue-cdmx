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
FILAS = ("primera", "ultima", "mayor", "total")
LADOS = ("a", "b")
ORIGENES = ("historia", "explorador", "analista")

# Medidas que una cifra de la narrativa puede nombrar (vocabulario cerrado). Cuáles existen en un estado
# concreto lo decide la vista exacta.
MEDIDAS = (
    "establecimientos", "establecimientos_seleccion", "locales_declarados", "estaciones", "estacion",
    "giro_dominante", "lugar", "macrosector", "participacion", "participacion_giro", "micronegocios", "nombre", "tipo",
)

# Huecos que llena el motor y no hay que declarar.
HUECOS_RESERVADOS = ("territorio", "fecha_corte", "edicion")
# Huecos que llena el motor solo en algunas escenas: `{radio}` es `escena.radio_m`.
HUECOS_POR_ESCENA = {"corredores_metro": ("radio",)}

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
# Cada vista dice qué es una fila y en qué orden van, y cada medida qué significa en esa vista y si tiene fila
# `total`. Así una cifra no puede nombrar una medida que existe pero significa otra cosa (H12).
#
# Filas de una cifra:
#   primera, ultima  la primera y la última en el orden de filas de la vista
#   mayor            la fila con más establecimientos (en un ranking coincide con `primera`)
#   total            el total del territorio; solo para medidas con total
#   {clave: ...}     la fila de esa clave (estación, conglomerado, subsector o macrosector)
VISTAS: dict[tuple[str, str], dict] = {
    ("ciudad_de_luz", "unico"): {
        "tipo_resultado": "territorial",
        "filas": "una por macrosector, de más a menos establecimientos",
        "medidas": {
            "establecimientos": {"total": True, "definicion": "establecimientos del macrosector; el total es el del "
                                                              "territorio"},
            "macrosector": {"total": False, "definicion": "nombre del macrosector"},
            "participacion": {"total": False, "definicion": "parte del macrosector en los establecimientos del "
                                                            "territorio"},
        },
    },
    ("corredores_metro", "linea"): {
        "tipo_resultado": "serie",
        "tablas": ("metro_linea", "metro_recorrido", "metro_estacion"),
        "filas": "una por estación de la línea, en orden de recorrido (la primera es una terminal)",
        "medidas": {
            "establecimientos": {"total": True, "definicion": "establecimientos cuya estación más cercana dentro del "
                                 "radio es esta. El total es la unión de radios de la línea (metro_linea): incluye "
                                 "los negocios más cercanos a otra línea, así que no es la suma de las filas"},
            "estaciones": {"total": True, "definicion": "estaciones de la línea; solo con fila total"},
            "estacion": {"total": False, "definicion": "nombre de la estación"},
            "giro_dominante": {"total": False, "definicion": "subsector SCIAN más frecuente alrededor de la estación"},
        },
    },
    ("corredores_metro", "ranking"): {
        "tipo_resultado": "ranking",
        "tablas": ("metro_estacion",),
        "filas": "una por estación, de más a menos establecimientos",
        "medidas": {
            "establecimientos": {"total": True, "definicion": "establecimientos cuya estación más cercana dentro del "
                                 "radio es esta; el total es la suma de las estaciones del territorio"},
            "micronegocios": {"total": True, "definicion": "establecimientos de 0 a 10 personas ocupadas alrededor de "
                                                           "la estación"},
            "lugar": {"total": False, "definicion": "puesto de la estación entre todas las de la ciudad"},
            "estacion": {"total": False, "definicion": "nombre de la estación"},
            "giro_dominante": {"total": False, "definicion": "subsector SCIAN más frecuente alrededor de la estación"},
            "participacion_giro": {"total": False, "definicion": "parte del giro dominante en los establecimientos "
                                                                 "de la estación"},
        },
    },
    ("ciudades_dentro", "exterior"): {
        "tipo_resultado": "ranking",
        "tablas": ("conglomerado",),
        "filas": "una por conglomerado, de más a menos establecimientos",
        "medidas": {
            "establecimientos": {"total": True, "definicion": "establecimientos del conglomerado"},
            "locales_declarados": {"total": True, "definicion": "locales que el DENUE declara en el conglomerado"},
            "nombre": {"total": False, "definicion": "nombre del conglomerado"},
            "tipo": {"total": False, "definicion": "tipo de conglomerado (mercado público, plaza comercial…)"},
        },
    },
    ("ciudades_dentro", "interior"): {
        "tipo_resultado": "perfil",
        "tablas": ("establecimiento",),
        "filas": "una por subsector SCIAN del conglomerado, de más a menos establecimientos",
        "medidas": {
            "establecimientos": {"total": True, "definicion": "establecimientos del subsector en el conglomerado"},
            "nombre": {"total": False, "definicion": "nombre del subsector"},
        },
    },
}
# La añade la vista exacta de Ciudades dentro (exterior) cuando hay selección.
MEDIDA_SELECCION = {"total": True, "definicion": "establecimientos de la selección en el conglomerado"}
TERRITORIOS_CON_RESUMEN = ("ciudad", "alcaldia", "colonia")

"""Definición de la herramienta "traducir_giro" para el ciclo de uso de herramientas de la API de Claude, y su
ejecución. Mismo molde que prototipos/03-resolver-lugar/herramienta.py.
"""
from traducir_giro import TraductorGiro

DEFINICION = {
    "name": "traducir_giro",
    "description": (
        "Convierte la forma común de nombrar un giro o tipo de negocio de la Ciudad de México (\"tiendita\", \"fonda\", "
        "\"donde arreglan celulares\") en clases SCIAN 2023 del DENUE. Úsala SIEMPRE antes de consultar datos por giro: "
        "nunca adivines códigos SCIAN. Devuelve estado: resuelto (una clase), grupo (varias clases que juntas forman "
        "el giro; consúltalas todas), ambiguo (pregunta al usuario cuál lectura quiere), sin_resultado (dilo tal cual, "
        "sin inventar) o no_es_giro (el texto no nombra una actividad; si es un lugar, usa resolver_lugar). "
        "Cada clase trae código, nombre y establecimientos vigentes. Lee `nota` y `confianza`: con confianza media "
        "o baja, confirma el giro con el usuario."),
    "input_schema": {
        "type": "object",
        "properties": {"consulta": {"type": "string", "description": "El giro tal como lo dijo el usuario, sin reformular."}},
        "required": ["consulta"],
    },
}


def ejecutar(traductor: TraductorGiro, args: dict) -> dict:
    """Ejecuta la herramienta y recorta la respuesta para el contexto del modelo."""
    r = traductor.traducir(args["consulta"])
    r.pop("candidatos", None)
    return r

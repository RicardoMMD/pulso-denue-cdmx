"""Definición de la herramienta "resolver_lugar" para el ciclo de uso de herramientas de la API de Claude (ver
docs/Síntesis, sección El Analista) y su ejecución. El modelo ligero (Haiku) la invoca con el texto del usuario;
la respuesta trae identificadores que el modelo capaz usa para consultar `semantic` y construir el estado de escena.
"""
from resolver_lugar import resolver_lugar

DEFINICION = {
    "name": "resolver_lugar",
    "description": (
        "Convierte una forma coloquial de nombrar un lugar de la Ciudad de México en identificadores territoriales. "
        "Entiende colonias y zonas (\"la Roma\", \"Polanco\"), alcaldías y sus apodos (\"GAM\"), estaciones y líneas del "
        "Metro, mercados y plazas, calles, y relaciones como \"cerca del metro Balderas\" o \"a 10 minutos del Zócalo\". "
        "Úsala SIEMPRE antes de consultar datos de un lugar: nunca adivines claves territoriales. "
        "Devuelve estado: resuelto (un lugar), grupo (varios que juntos forman el lugar, p. ej. Roma Norte y Roma Sur), "
        "ambiguo (pregunta al usuario cuál de los candidatos), sin_resultado o fuera_de_cdmx (dilo tal cual, sin inventar). "
        "Si trae `relacion: cerca_de`, usa `ancla` y `radio_m` con ST_DWithin. Lee `nota` y `confianza`: con confianza "
        "media o baja confirma el lugar con el usuario."),
    "input_schema": {
        "type": "object",
        "properties": {"consulta": {"type": "string", "description": "El lugar tal como lo dijo el usuario, sin reformular."}},
        "required": ["consulta"],
    },
}


def ejecutar(conn, args: dict, max_candidatos: int = 8) -> dict:
    """Ejecuta la herramienta y recorta la respuesta para el contexto del modelo."""
    r = resolver_lugar(conn, args["consulta"])
    r["candidatos"] = r["candidatos"][:max_candidatos]
    return r

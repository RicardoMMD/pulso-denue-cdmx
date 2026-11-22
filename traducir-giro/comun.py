"""Rutas, registro de modelos y funciones compartidas del subproyecto.

Este módulo no importa torch: lo usan también los scripts que no cargan modelos.
"""
import json
import os
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DATOS = RAIZ / "datos"
BANCOS = RAIZ / "bancos"
VECTORES = RAIZ / "vectores"      # no versionado
MODELOS_DIR = RAIZ / "modelos"    # no versionado: aquí quedan las descargas de Hugging Face
RESULTADOS = RAIZ / "resultados"

TIPOS = ("calle", "descripcion", "error_dedo", "no_es_giro")
NOMBRE_TIPO = {
    "calle": "Palabra de la calle",
    "descripcion": "Descripción libre",
    "error_dedo": "Con error de dedo",
    "no_es_giro": "No es un giro",
}

# Cada modelo se usa como lo recomienda su autor. La revisión fija el contenido exacto que se baja.
# `consulta` y `documento` son el texto que se antepone al término y a la clase.
MODELOS = {
    "qwen3": {
        "repo": "Qwen/Qwen3-Embedding-0.6B",
        "revision": "97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3",
        "licencia": "Apache 2.0",
        "disco_gb": 1.2,
        "acceso": "libre",
        "consulta": "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery:",
        "documento": None,
        "fuente_config": "config_sentence_transformers.json del modelo (15 nov 2026)",
    },
    "gemma": {
        "repo": "google/embeddinggemma-300m",
        "revision": "57c266a740f537b4dc058e1b0cda161fd15afa75",
        "licencia": "Gemma (con condiciones de uso)",
        "disco_gb": 1.2,
        "acceso": "restringido: aceptar términos en Hugging Face y poner HF_TOKEN en .env",
        "consulta": "task: search result | query: ",
        "documento": "title: none | text: ",
        "fuente_config": "config_sentence_transformers.json del modelo, comparado con descargar.py (15 nov 2026)",
    },
    "e5-small": {
        "repo": "intfloat/multilingual-e5-small",
        "revision": "614241f622f53c4eeff9890bdc4f31cfecc418b3",
        "licencia": "MIT",
        "disco_gb": 0.5,
        "acceso": "libre",
        "consulta": "query: ",
        "documento": "passage: ",
        "fuente_config": "ficha del modelo (el modelo no trae la configuración en archivo)",
    },
}


def sin_red():
    """Impide que cargar un modelo dispare una descarga. Las descargas solo ocurren en descargar.py."""
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"


def ruta_modelo(nombre):
    return MODELOS_DIR / nombre


def cargar_modelo(nombre):
    """Carga un modelo ya descargado, sin tarjeta gráfica y sin tocar la red."""
    sin_red()
    ruta = ruta_modelo(nombre)
    if not (ruta / "modules.json").exists():
        raise SystemExit(f"El modelo '{nombre}' no está descargado. Corre: uv run python descargar.py {nombre}")
    import torch
    from sentence_transformers import SentenceTransformer
    # fp32 explícito: Qwen3 viene en bf16 y, sin esto, se carga así y es ~3 veces más lento en procesador
    # (medido el 15 nov 2026). Los tres modelos se miden con la misma precisión para que C4 sea comparable.
    return SentenceTransformer(str(ruta), device="cpu", model_kwargs={"dtype": torch.float32})


def codificar(modelo, nombre, textos, papel):
    """Vectores normalizados. `papel` es 'consulta' o 'documento'."""
    prefijo = MODELOS[nombre][papel]
    return modelo.encode(list(textos), prompt=prefijo, normalize_embeddings=True,
                         batch_size=16, show_progress_bar=False)


def normalizar(texto):
    """Mayúsculas y sin acentos (la ñ se conserva)."""
    texto = texto.upper().replace("Ñ", "\0")
    texto = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    return texto.replace("\0", "Ñ")


def leer_catalogo():
    ruta = DATOS / "clases.json"
    if not ruta.exists():
        raise SystemExit("Falta datos/clases.json. Corre: make catalogo (necesita túnel)")
    return json.loads(ruta.read_text(encoding="utf-8"))


def leer_banco(nombre):
    ruta = BANCOS / f"{nombre}.json"
    if not ruta.exists():
        raise SystemExit(f"Falta bancos/{nombre}.json")
    return json.loads(ruta.read_text(encoding="utf-8"))


# --- Texto por clase -------------------------------------------------------------------------
# Los tres modelos ven el mismo texto. Las variantes se comparan solo en el banco de ajuste.

def texto_simple(clase):
    """Nombre de la clase y su jerarquía."""
    partes = [clase["nombre_clase"]]
    for campo in ("nombre_rama", "nombre_subsector", "nombre_sector"):
        if clase[campo] and clase[campo] not in partes:
            partes.append(clase[campo])
    return ". ".join(partes)


def texto_palabras(clase, cuantas=8):
    """El texto simple más las palabras frecuentes de los nombres comerciales de la clase."""
    palabras = [p["palabra"].lower() for p in clase.get("palabras_frecuentes", [])[:cuantas]]
    base = texto_simple(clase)
    return f"{base}. Nombres comunes: {', '.join(palabras)}" if palabras else base


VARIANTES = {"simple": texto_simple, "palabras": texto_palabras}

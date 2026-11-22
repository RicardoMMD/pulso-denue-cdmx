"""Descarga un modelo de Hugging Face a modelos/ (no versionado). Es el único script que usa la red.

Sin --si solo dice qué bajaría. Cada descarga se pide por separado.

Uso:
  uv run python descargar.py              lista los modelos y su estado
  uv run python descargar.py qwen3        dice qué bajaría
  uv run python descargar.py qwen3 --si   lo baja

EmbeddingGemma necesita aceptar los términos en su ficha y un HF_TOKEN de lectura en el .env del repo.
"""
import json
import os
import sys

from comun import MODELOS, ruta_modelo


def estado(nombre):
    return "descargado" if (ruta_modelo(nombre) / "modules.json").exists() else "sin descargar"


def listar():
    for nombre, m in MODELOS.items():
        print(f"{nombre:9} {m['repo']:32} ~{m['disco_gb']} GB  {m['licencia']:30} {estado(nombre)}")
        if m["acceso"] != "libre":
            print(f"{'':9} acceso {m['acceso']}")


def comparar_config(nombre):
    """Avisa si las instrucciones anotadas en comun.py difieren de las que trae el modelo."""
    ruta = ruta_modelo(nombre) / "config_sentence_transformers.json"
    if not ruta.exists():
        print("El modelo no trae instrucciones en archivo; se usan las de su ficha.")
        return
    reales = json.loads(ruta.read_text(encoding="utf-8")).get("prompts", {})
    for papel, clave in (("consulta", "query"), ("documento", "document")):
        anotada, real = MODELOS[nombre][papel] or "", reales.get(clave) or ""
        marca = "igual" if anotada == real else "DISTINTA: corregir comun.py antes de medir"
        print(f"instrucción de {papel}: {marca}\n  anotada: {anotada!r}\n  modelo:  {real!r}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        return listar()
    nombre = args[0]
    if nombre not in MODELOS:
        raise SystemExit(f"Modelo desconocido: {nombre}. Opciones: {', '.join(MODELOS)}")
    m = MODELOS[nombre]
    print(f"{m['repo']} · revisión {m['revision'][:10]} · ~{m['disco_gb']} GB · licencia {m['licencia']}\n"
          f"fuente: https://huggingface.co/{m['repo']}\ndestino: {ruta_modelo(nombre)}")
    if "--si" not in sys.argv:
        print("No se bajó nada. Para bajarlo, repite con --si.")
        return
    from huggingface_hub import snapshot_download
    snapshot_download(m["repo"], revision=m["revision"], local_dir=ruta_modelo(nombre),
                      token=os.environ.get("HF_TOKEN") or None,
                      # Solo lo que usa sentence-transformers; fuera las copias en otros formatos.
                      ignore_patterns=["onnx/*", "openvino/*", "*.onnx", "*.bin", "*.h5", "*.ot", "*.msgpack"])
    print("descargado")
    comparar_config(nombre)


if __name__ == "__main__":
    main()

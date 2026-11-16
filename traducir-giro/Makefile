# Traducir giro — comandos del subproyecto. Se corren desde este directorio.
# Solo `catalogo` necesita túnel y .env; solo `descargar` usa la red. Nada escribe en la base.

SHELL    := /bin/bash
ENV      := set -a && . ../.env && set +a
VARIANTE ?= simple

.PHONY: catalogo validar modelos descargar vectores ajuste ciego

## catalogo: exporta las clases SCIAN a datos/clases.json (solo lectura, necesita túnel)
catalogo:
	@(exec 3<>/dev/tcp/127.0.0.1/55432) 2>/dev/null \
	  || { echo "Túnel cerrado. Ábrelo con: ssh -f -N -L 55432:localhost:5433 vps"; exit 1; }
	@$(ENV) && uv run --group base python exportar_catalogo.py

## validar: forma de los bancos y clases válidas (sin base ni modelos)
validar:
	@python3 validar_bancos.py && echo "validar: OK"

## modelos: lista los modelos y si están descargados
modelos:
	@uv run python descargar.py

## descargar MODELO=qwen3: baja un modelo de Hugging Face a modelos/ (pide HF_TOKEN para gemma)
descargar:
	@{ [ ! -f ../.env ] || $(ENV); } && uv run python descargar.py $(MODELO) --si

## vectores: clases → vectores con todos los modelos descargados (VARIANTE=simple|palabras)
vectores:
	@uv run python vectorizar.py --variante $(VARIANTE)

## ajuste: vectores + banco de ajuste + tabla en resultados/ajuste-$(VARIANTE).md
ajuste: validar vectores
	@uv run python evaluar.py ajuste --variante $(VARIANTE)

## ciego: banco ciego, UNA sola vez, con los umbrales confirmados
ciego: validar
	@uv run python evaluar.py ciego --variante $(VARIANTE) --confirmo-ciego

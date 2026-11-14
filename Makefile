# Pulso DENUE CDMX — comandos del repo.
# Todo lo que toca la base necesita el túnel SSH (localhost:55432 -> VPS:5433) y el .env.
# Solo hay una base: `make build` reescribe tablas reales; `make verify` solo lee.

SHELL    := /bin/bash
ENV      := set -a && . ../.env && set +a
DBT_ARGS := --project-dir ../dbt --profiles-dir ../dbt
PY_SRC   := pipeline/*.py prototipos/02-renderizador/*.py prototipos/03-resolver-lugar/*.py investigaciones-experimentos/01-api-denue/*.py

.PHONY: verify check tunel test build eval-lugar

## verify: comprobación completa antes de dar algo por terminado (solo lectura)
verify: check tunel test
	@echo "verify: OK"

## check: sin base de datos — sintaxis de Python y JS, y dbt parse
check:
	@cd pipeline && uv run python -m py_compile $(addprefix ../,$(PY_SRC))
	@node --check prototipos/02-renderizador/src/main.js
	@cd pipeline && $(ENV) && uv run dbt parse $(DBT_ARGS) --quiet
	@echo "check: OK"

## tunel: falla si el túnel a la base no está abierto
tunel:
	@(exec 3<>/dev/tcp/127.0.0.1/55432) 2>/dev/null \
	  || { echo "Túnel cerrado. Ábrelo con: ssh -f -N -L 55432:localhost:5433 vps"; exit 1; }

## test: las 110 pruebas de dbt (solo lectura, ~90 s)
test:
	@cd pipeline && $(ENV) && uv run dbt test $(DBT_ARGS) --quiet

## build: RECONSTRUYE staging, core y semantic en la base real. No va en verify.
build: tunel
	@cd pipeline && $(ENV) && uv run dbt build $(DBT_ARGS)

## eval-lugar: banco del prototipo 3 (reescribe resultados.md)
eval-lugar: tunel
	@cd pipeline && $(ENV) && PYTHONPATH=../prototipos/03-resolver-lugar uv run python ../prototipos/03-resolver-lugar/evaluar.py

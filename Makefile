# Pulso DENUE CDMX — comandos del repo.
# Todo lo que toca la base necesita el túnel SSH (localhost:55432 -> VPS:5433) y el .env.
# Solo hay una base: `make build` reescribe tablas reales; `make verify` solo lee.

SHELL    := /bin/bash
ENV      := set -a && . ../.env && set +a
# Para `check` y `ci`: usa el .env si existe y, si no (GitHub Actions), variables de mentira. `dbt parse` no se conecta.
ENV_CHECK := set -a && { [ ! -f ../.env ] || . ../.env; } && : $${PULSO_OWNER_USER:=ci} $${PULSO_OWNER_PASSWORD:=ci} && set +a
DBT_ARGS := --project-dir ../dbt --profiles-dir ../dbt
PY_SRC   := pipeline/*.py prototipos/02-renderizador/*.py prototipos/03-resolver-lugar/*.py investigaciones-experimentos/01-api-denue/*.py backend/contracts/*.py traducir-giro/*.py
# Lo que genera backend/contracts/generar.py: no se edita a mano.
GENERADOS := backend/contracts/escena.v1.json backend/contracts-ts/escena.v1.d.ts backend/contracts-ts/validar-estructura.js
EDICION  ?= 2026-05

.PHONY: verify ci check contratos diseno generado-al-dia tunel test build referencias eval-lugar

## verify: comprobación completa antes de dar algo por terminado (solo lectura)
verify: ci tunel test
	@echo "verify: OK"

## ci: lo que corre GitHub Actions, sin base de datos: check + contratos + diseno
ci: check contratos diseno
	@echo "ci: OK"

## check: sin base de datos — sintaxis de Python y JS, y dbt parse
check:
	@cd pipeline && uv run python -m py_compile $(addprefix ../,$(PY_SRC))
	@python3 traducir-giro/validar_bancos.py
	@node --check prototipos/02-renderizador/src/main.js
	@node --check laboratorio/src/laboratorio.js
	@node --check laboratorio/src/giros.js
	@node --check diseno/generar.mjs
	@cd pipeline && $(ENV_CHECK) && uv run dbt parse $(DBT_ARGS) --quiet
	@echo "check: OK"

backend/contracts-ts/node_modules: backend/contracts-ts/package-lock.json
	@cd backend/contracts-ts && npm ci --silent && touch node_modules

## contratos: contrato de escena sin base — pytest, pruebas de Node, historias y archivos generados al día
contratos: backend/contracts-ts/node_modules
	@cd backend && uv run pytest -q
	@cd backend/contracts-ts && npm test --silent
	@cd backend && uv run python -m contracts.validar_historias
	@$(MAKE) --no-print-directory generado-al-dia
	@echo "contratos: OK"

## diseno: pruebas de los tokens del sistema visual (contraste, macrosectores, generado al día), sin base
diseno:
	@node --test diseno/test/*.test.mjs >/dev/null || { node --test diseno/test/*.test.mjs; exit 1; }
	@echo "diseno: OK"

## generado-al-dia: regenera escena.v1.json, los tipos TS y el validador Ajv, y falla si algo cambió
generado-al-dia: backend/contracts-ts/node_modules
	@antes=$$(sha256sum $(GENERADOS)) && \
	  (cd backend && uv run python -m contracts.generar >/dev/null) && \
	  despues=$$(sha256sum $(GENERADOS)) && \
	  { [ "$$antes" = "$$despues" ] || { echo "Los archivos generados estaban desactualizados; ya se regeneraron. Revísalos y súbelos."; exit 1; }; }

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

## referencias: vuelve a exportar el catálogo de referencias de la edición (EDICION=2026-05) desde semantic (solo lectura)
referencias: tunel
	@cd backend && $(ENV) && uv run --group base python -m contracts.exportar_referencias $(EDICION)

## eval-lugar: banco del prototipo 3 (reescribe resultados.md)
eval-lugar: tunel
	@cd pipeline && $(ENV) && PYTHONPATH=../prototipos/03-resolver-lugar uv run python ../prototipos/03-resolver-lugar/evaluar.py

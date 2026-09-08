# npm-style shortcuts for this Python + Nx repo
# Usage: make start

ORG ?= household
PYTHON ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)
export PYTHONPATH := python

.PHONY: help install install-web setup-ollama start-ollama stop-ollama ingest ui ui-streamlit api web start ask

help:
	@echo "Available commands (like package.json scripts):"
	@echo "  make install       Install Python deps into .venv"
	@echo "  make install-web   Install Nx/React deps (npm install)"
	@echo "  make setup-ollama  Pull Ollama models (once)"
	@echo "  make start         Start Ollama + ingest + API + React UI"
	@echo "  make start-ollama  Start Ollama only"
	@echo "  make stop-ollama   Stop Ollama"
	@echo "  make ingest        Ingest org documents (ORG=household)"
	@echo "  make api           FastAPI only (:8000)"
	@echo "  make web           Nx React UI only (:4200)"
	@echo "  make ui-streamlit  Legacy Streamlit UI"
	@echo "  make ask Q='...'   One-shot agent question"

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

install-web:
	npm install

setup-ollama:
	./scripts/setup-ollama.sh

start-ollama:
	./scripts/start-ollama.sh

stop-ollama:
	./scripts/stop-ollama.sh

ingest:
	$(PYTHON) -m rag.ingest --org $(ORG)

ui: web

ui-streamlit:
	$(PYTHON) run_ui.py

api:
	$(PYTHON) run_api.py

web:
	npx nx serve web

start:
	./scripts/dev.sh $(ORG)

ask:
	@test -n "$(Q)" || (echo 'Usage: make ask Q="What is PMEGP?"' >&2; exit 1)
	$(PYTHON) -m agent.run --org $(ORG) "$(Q)"

# Makefile for V-Lab Digital Library Backend
# Usage: make <target>

PYTHON ?= python3
VENV_DIR = .venv
PY = $(VENV_DIR)/bin/python
PIP = $(PY) -m pip
UVICORN = $(PY) -m uvicorn

.PHONY: help venv install install-dev freeze db-up db-down run run-prod clean
.PHONY: smoke-test

help:
	@echo "Available targets:"
	@echo "  venv        - create a virtualenv in $(VENV_DIR)"
	@echo "  install     - install runtime dependencies from requirements.txt into the venv"
	@echo "  freeze      - freeze venv packages into requirements.txt"
	@echo "  db-up       - start MySQL via docker-compose"
	@echo "  db-down     - stop MySQL docker-compose service"
	@echo "  run         - run development server (uvicorn --reload)"
	@echo "  run-prod    - run production server (uvicorn)"
	@echo "  clean       - remove virtualenv and python cache files"

venv:
	@echo "Creating virtualenv in $(VENV_DIR) if missing..."
	@test -d $(VENV_DIR) || $(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtualenv ready. Activate with: source $(VENV_DIR)/bin/activate"

install: venv
	@echo "Installing dependencies into $(VENV_DIR)..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

freeze: venv
	@echo "Freezing installed packages to requirements.txt"
	$(PIP) freeze | sort > requirements.txt

db-up:
	@echo "Starting MySQL (docker-compose up -d)"
	docker-compose up -d
	@echo "Initializing database schema (app.db.initialize_db as module)"
	$(PY) -m app.db.initialize_db


.PHONY: tests
tests:
	@echo "Starting test MySQL (docker-compose -f docker-compose.test.yml up -d)"
	# Start the test DB service (reads .env.test)
	docker-compose -f docker-compose.test.yml up -d
	@echo "Running tests (conftest.py will handle waiting/creation of the test DB)"
	# Run pytest; conftest will read .env.test and wait/create the DB as needed
	$(PY) -m pytest -q
	@echo "Tearing down test compose stack"
	docker-compose -f docker-compose.test.yml down -v

init-db: venv
	@echo "Run database initialization script"
	$(PY) -m app.db.initialize_db

db-down:
	@echo "Stopping MySQL (docker-compose down)"
	docker-compose down -v

run: venv
	@echo "Starting development server (reload)..."
	$(UVICORN) app.main:app --reload --port 8000

smoke-test: venv
	@echo "Running smoke tests against http://localhost:8000"
	@$(PY) smoke_test.py

run-prod: venv
	@echo "Starting production server..."
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

clean:
	@echo "Removing virtualenv and Python cache files..."
	-rm -rf $(VENV_DIR)
	@echo "Removing __pycache__ directories..."
	-find . -type d -name '__pycache__' -prune -exec rm -rf '{}' + || true
	@echo "Removing .pyc files..."
	-find . -name "*.pyc" -delete || true

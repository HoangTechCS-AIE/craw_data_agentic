.PHONY: dev test run crawl release lint

VENV?=.venv
PYTHON?=python3

setup:
$(PYTHON) -m venv $(VENV)
$(VENV)/bin/pip install -U pip
$(VENV)/bin/pip install -r requirements.txt

dev: setup

run:
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

crawl:
python -m agent.orchestrator

test:
pytest -q

release:
git tag -f v1.0.0
git push --tags || true

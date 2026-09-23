# Makefile — task runner for the Quantum Computing Study Suite.
#
#   make            same as `make help`
#   make dev test   chain targets as usual
#
# Every target shells out to the repository's own scripts (setup.sh,
# tools/run_tests.sh, tools/verify_docs.py); nothing here reimplements them, so
# the Makefile and the documented command lines can never drift.
#
# Interpreter: the repo venv at .venv/bin/python when it exists, otherwise
# python3 from PATH.  Override with `make PYTHON=/path/to/python3.12 test`.
#
# Requires GNU make.  Recipes run under bash (SHELL below).

SHELL := /bin/bash
.DEFAULT_GOAL := help

# Absolute repo root, taken from this file's own location, so `make -C` and
# `make -f` work from anywhere.
ROOT := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))

VENV_PYTHON := $(wildcard $(ROOT)/.venv/bin/python)
PYTHON ?= $(if $(VENV_PYTHON),$(VENV_PYTHON),python3)

# Extra arguments forwarded to the underlying tool, e.g.
#   make test ARGS="-m slow"
#   make docs ARGS="--no-snippets"
#   make launch ARGS="--status"
ARGS ?=

# Paths `make clean` deletes.  All of them are generated; none is tracked by
# git (verify with: git ls-files --error-unmatch <path>).
CLEAN_DIRS := \
	$(ROOT)/build \
	$(ROOT)/dist \
	$(ROOT)/exports \
	$(ROOT)/htmlcov \
	$(ROOT)/.mypy_cache \
	$(ROOT)/.ruff_cache

.PHONY: help setup dev test docs lint coverage notebooks export launch clean

# ---------------------------------------------------------------------------
help: ## List the available targets (default)
	@echo "Quantum Computing Study Suite"
	@echo
	@echo "Usage: make <target> [PYTHON=...] [ARGS=...]"
	@echo
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "} {printf "  %-10s %s\n", $$1, $$2}'
	@echo
	@echo "Python: $(PYTHON)"

# ---------------------------------------------------------------------------
setup: ## Create .venv and install runtime requirements (setup.sh)
	@bash $(ROOT)/setup.sh $(ARGS)

dev: ## setup plus pytest, notebook tooling and a Jupyter kernel (setup.sh --dev)
	@bash $(ROOT)/setup.sh --dev $(ARGS)

# ---------------------------------------------------------------------------
test: ## Run every test suite: root tests/ plus one process per app
	@bash $(ROOT)/tools/run_tests.sh $(ARGS)

docs: ## Verify the docs corpus and lesson plans (structure, links, snippets)
	@cd $(ROOT) && $(PYTHON) tools/verify_docs.py --all $(ARGS)

lint: ## Type-check the console tools with mypy ([tool.mypy] in pyproject.toml)
	@if ! $(PYTHON) -c 'import mypy' >/dev/null 2>&1; then \
		echo "make lint: mypy is not installed for $(PYTHON)"; \
		echo "           install it with: $(PYTHON) -m pip install mypy"; \
		exit 1; \
	fi
	@cd $(ROOT) && $(PYTHON) -m mypy $(ARGS)

coverage: ## Run the root suite under coverage ([tool.coverage] in pyproject.toml)
	@if ! $(PYTHON) -c 'import coverage' >/dev/null 2>&1; then \
		echo "make coverage: coverage is not installed for $(PYTHON)"; \
		echo "               install it with: $(PYTHON) -m pip install coverage"; \
		exit 1; \
	fi
	@# Headless Qt, as tools/run_tests.sh does.  The study data directory
	@# needs no guard here: tests/conftest.py points QUANTUM_STUDY_DATA_DIR at
	@# a fresh temp dir at import time, before any test runs.
	@cd $(ROOT) \
		&& export QT_QPA_PLATFORM=$${QT_QPA_PLATFORM:-offscreen} \
		&& $(PYTHON) -m coverage erase \
		&& $(PYTHON) -m coverage run -m pytest $(ARGS) \
		&& $(PYTHON) -m coverage combine \
		&& $(PYTHON) -m coverage report

# ---------------------------------------------------------------------------
notebooks: ## Execute every notebook in notebooks/ with nbclient (a smoke test)
	@if ! $(PYTHON) -c 'import nbclient, nbformat' >/dev/null 2>&1; then \
		echo "make notebooks: nbclient/nbformat are not installed for $(PYTHON)"; \
		echo "                install them with: make dev"; \
		exit 1; \
	fi
	@# ipykernel 7 prints a "running over TCP without encryption" warning per
	@# kernel.  It is harmless for a local run and deliberately not filtered:
	@# swallowing the kernel's stderr would swallow real execution errors too.
	@set -e; for nb in $(ROOT)/notebooks/*.ipynb; do \
		echo "==> $$(basename $$nb)"; \
		$(PYTHON) -c 'import sys, nbformat; from nbclient import NotebookClient; p = sys.argv[1]; nb = nbformat.read(p, as_version=4); NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": sys.argv[2]}}).execute()' \
			"$$nb" "$(ROOT)/notebooks"; \
	done
	@echo "notebooks: all executed cleanly (outputs were not written back)"

# tools/export_cards.py is maintained separately from this Makefile.  The guard
# below exists because the target was wired up before that script landed: in a
# checkout that predates it, `make export` says so in one line instead of
# raising a bare "can't open file" traceback.  Writes into exports/, which
# `make clean` removes.
export: ## Export the card / question banks to shareable files
	@if [[ ! -f $(ROOT)/tools/export_cards.py ]]; then \
		echo "make export: tools/export_cards.py does not exist yet."; \
		echo "             This target is wired up ahead of that script landing."; \
		exit 1; \
	fi
	@cd $(ROOT) && $(PYTHON) tools/export_cards.py --all $(ARGS)

launch: ## Open the launcher GUI (make launch ARGS=--list for the CLI)
	@cd $(ROOT) && $(PYTHON) launch.py $(ARGS)

# ---------------------------------------------------------------------------
clean: ## Delete caches, exports and build artefacts (never anything tracked)
	@echo "removing __pycache__/ and .pytest_cache/ trees..."
	@find $(ROOT) -path $(ROOT)/.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf {} +
	@find $(ROOT) -path $(ROOT)/.venv -prune -o -type d -name '.pytest_cache' -print -exec rm -rf {} +
	@# -exec rm, not -delete: -delete implies -depth, and -depth makes -prune
	@# a no-op, so GNU find refuses the combination outright.
	@find $(ROOT) -path $(ROOT)/.venv -prune -o -type f -name '*.py[co]' -print -exec rm -f {} +
	@for d in $(CLEAN_DIRS) $(ROOT)/*.egg-info; do \
		[[ -e $$d ]] && { echo "$$d"; rm -rf "$$d"; }; \
	done; true
	@for f in $(ROOT)/.coverage $(ROOT)/.coverage.*; do \
		[[ -e $$f ]] && { echo "$$f"; rm -f "$$f"; }; \
	done; true
	@echo "clean: done"

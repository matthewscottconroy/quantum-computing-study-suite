#!/usr/bin/env bash
# tools/run_tests.sh — run the tests.  One pytest run covers everything: the
# root suite (tests/) and every app's own suite (quantum_study/<app>/tests/).
#
#   tools/run_tests.sh                          # everything except "slow" tests
#   tools/run_tests.sh -m slow                  # only the slow ones
#   tools/run_tests.sh quantum_study/exam_sim   # one app
#   tools/run_tests.sh tests -k coach -x        # any pytest arguments
#
# It only finds the interpreter and makes the run headless; pytest.ini and the
# root conftest.py do the rest (including keeping every test out of the real
# ~/.local/share/quantum-study).  Exit status is pytest's, or 2 when no Python
# with pytest can be found.
set -u -o pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
else
  PY="$(command -v python3 || true)"
  if [[ -z "$PY" ]]; then
    echo "run_tests: no .venv/bin/python and no python3 on PATH" >&2
    exit 2
  fi
  echo "run_tests: .venv not found, falling back to $PY" >&2
fi
if ! "$PY" -c 'import pytest' 2>/dev/null; then
  echo "run_tests: pytest is not importable by $PY" \
       "(pip install -r requirements-dev.txt, or ./setup.sh --dev)" >&2
  exit 2
fi

export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}"
export MPLBACKEND="${MPLBACKEND:-Agg}"
cd "$ROOT" && exec "$PY" -m pytest "$@"

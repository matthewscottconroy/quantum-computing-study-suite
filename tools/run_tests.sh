#!/usr/bin/env bash
# tools/run_tests.sh — run every test suite in the repository.
#
#   root     tests/          coach.py, dashboard.py, launch.py, tools/verify_docs.py
#   <app>/   <app>/tests/    one pytest process per app (several apps have
#                            clashing top-level packages: problems/, core/, ui/)
#
# Suites are discovered dynamically: every <repo>/<dir>/pytest.ini whose
# directory also contains tests/ is a suite.  The discovered list is printed
# before anything runs, so a suite that moved or a stray pytest.ini is visible.
#
# Usage:
#   tools/run_tests.sh              # fast tests (each pytest.ini deselects "slow")
#   tools/run_tests.sh -m slow      # only the slow tests (root + qiskit-dojo today);
#                                   # suites that select none are reported SKIP
#   tools/run_tests.sh -x -vv       # extra args are forwarded to every pytest run
#                                   # (don't forward -q: every pytest.ini already has
#                                   # it, and -qq silences the summary line we parse)
#
# Prints "PASS|FAIL|SKIP <suite> (<n> tests, <t>s)" per suite plus a final tally.
# A suite only counts as PASS when pytest exits 0 *and* its summary line
# reports at least one test (passed/failed/... or, with --collect-only,
# "N tests collected"); exit 0 with nothing parsed is reported as FAIL so a
# changed summary format or an accidental deselect-everything can never turn
# the whole run silently green.  pytest exit 5 (nothing collected, or every
# test deselected) is SKIP only when the command line carries a selection
# flag (-m / -k / --deselect) -- otherwise it is FAIL -- and the run as a
# whole still fails unless at least one suite PASSed, so a selection that
# matches nothing anywhere cannot exit 0.
# Exit status: 0 when no suite fails and at least one passes; 1 if any suite
# fails, collects no tests, reports 0 tests, or no suite ran anything; 2 if
# no Python interpreter with pytest can be found.
# Requires bash 4+ (mapfile, PIPESTATUS).  grep -E/-o, awk, find
# -mindepth/-maxdepth and mktemp are used as both GNU and BSD userlands ship
# them; GNU date's %N gives sub-second timings, other dates fall back to
# whole seconds.

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

# Headless Qt for the app suites; never let a test touch the real study data.
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}"
CLEANUP=()
if [[ -z "${QUANTUM_STUDY_DATA_DIR:-}" ]]; then
  SCRATCH_DATA="$(mktemp -d "${TMPDIR:-/tmp}/quantum-study-tests.XXXXXX")"
  export QUANTUM_STUDY_DATA_DIR="$SCRATCH_DATA"
  CLEANUP+=("$SCRATCH_DATA")
fi
LOG="$(mktemp "${TMPDIR:-/tmp}/run_tests.XXXXXX")"
CLEANUP+=("$LOG")
cleanup() { rm -rf ${CLEANUP[@]+"${CLEANUP[@]}"}; }
trap cleanup EXIT

EXTRA=("$@")
# With a selection flag on the command line, "nothing selected" (pytest exit
# 5) is the expected outcome for suites that have no matching tests, so those
# are reported SKIP rather than FAIL.
SELECTING=0
for arg in ${EXTRA[@]+"${EXTRA[@]}"}; do
  case "$arg" in
    -m|-k|-m?*|-k?*|--deselect|--deselect=*) SELECTING=1 ;;
  esac
done
RESULTS=()
N_PASS=0
N_FAIL=0
N_SKIP=0

# pytest's final line, e.g. "12 passed, 1 deselected in 0.34s",
# "==== 1 failed, 11 passed in 0.5s ====" (any verbosity >= 0), "no tests ran
# in 0.01s", "20 deselected in 0.01s" or, under --collect-only, "213/214 tests
# collected (1 deselected) in 0.04s" / "no tests collected (20 deselected) in
# 0.01s".  Kept in variables so the bash =~ tests below need no escaping.
RE_SUMMARY='(^|[ =])[0-9]+ (passed|failed|errors?|skipped|xfailed|xpassed|deselected|warnings?)([ ,]|$)|(^|[ =])no tests (ran|collected)|(^|[ =])[0-9]+(/[0-9]+)? tests? collected'
RE_COLLECTED='(^|[ =])([0-9]+)(/[0-9]+)? tests? collected'
RE_DESELECTED='([0-9]+) deselected'

now_s() {
  local t
  t="$(date +%s.%N 2>/dev/null || true)"
  [[ "$t" =~ ^[0-9]+\.[0-9]+$ ]] || t="$(date +%s)"
  printf '%s' "$t"
}

run_suite() {   # run_suite <label> <dir>
  local label="$1" dir="$2"
  local start end secs rc summary n noun status detail line
  echo
  echo "=================== $label  ($dir) ==================="
  start="$(now_s)"
  ( cd "$dir" && "$PY" -m pytest ${EXTRA[@]+"${EXTRA[@]}"} ) 2>&1 | tee "$LOG"
  rc=${PIPESTATUS[0]}
  end="$(now_s)"
  secs="$(awk -v a="$start" -v b="$end" 'BEGIN { printf "%.1f", b - a }')"
  summary="$(grep -E "$RE_SUMMARY" "$LOG" | tail -n 1)"
  n="$(printf '%s\n' "$summary" \
       | grep -oE '[0-9]+ (passed|failed|errors?|skipped|xfailed|xpassed)' \
       | awk '{ s += $1 } END { print s + 0 }')"
  noun="tests"
  if [[ $n -eq 0 && "$summary" =~ $RE_COLLECTED ]]; then
    n="${BASH_REMATCH[2]}"; noun="tests collected"
  fi
  if [[ $rc -eq 0 && $n -gt 0 ]]; then
    status="PASS"; N_PASS=$((N_PASS + 1))
  elif [[ $rc -eq 5 && $SELECTING -eq 1 ]]; then
    status="SKIP"; N_SKIP=$((N_SKIP + 1))
  else
    status="FAIL"; N_FAIL=$((N_FAIL + 1))
  fi
  detail="$n $noun, ${secs}s"
  if [[ $rc -eq 5 ]]; then
    if [[ "$summary" =~ $RE_DESELECTED ]]; then
      detail="no tests selected (${BASH_REMATCH[1]} deselected), ${secs}s"
    else
      detail="no tests collected, ${secs}s"
    fi
  elif [[ $rc -ne 0 ]]; then
    detail="$detail, exit $rc"
  elif [[ $n -eq 0 ]]; then
    detail="0 tests ran or summary line not parsed, ${secs}s"
  fi
  line="$status $label ($detail)"
  echo "$line"
  RESULTS+=("$line")
}

# ---- discover suites (root + every <dir>/pytest.ini with a tests/ dir) ------
SUITE_LABELS=()
SUITE_DIRS=()
if [[ -f "$ROOT/pytest.ini" && -d "$ROOT/tests" ]]; then
  SUITE_LABELS+=("root"); SUITE_DIRS+=("$ROOT")
else
  echo "run_tests: no $ROOT/pytest.ini + tests/ — skipping root suite" >&2
fi
mapfile -t INIS < <(find "$ROOT" -mindepth 2 -maxdepth 2 -name pytest.ini \
                      -not -path "$ROOT/.venv/*" -not -path "$ROOT/.git/*" | sort)
for ini in ${INIS[@]+"${INIS[@]}"}; do
  dir="$(dirname "$ini")"
  if [[ ! -d "$dir/tests" ]]; then
    echo "run_tests: ignoring $ini (no $dir/tests/ directory)" >&2
    continue
  fi
  SUITE_LABELS+=("$(basename "$dir")"); SUITE_DIRS+=("$dir")
done

echo "run_tests: python = $PY"
echo "run_tests: QUANTUM_STUDY_DATA_DIR = $QUANTUM_STUDY_DATA_DIR"
echo "run_tests: ${#SUITE_LABELS[@]} suite(s) = ${SUITE_LABELS[*]}"
if [[ ${#SUITE_LABELS[@]} -eq 0 ]]; then
  echo "run_tests: no test suites found under $ROOT" >&2
  exit 1
fi

for i in "${!SUITE_LABELS[@]}"; do
  run_suite "${SUITE_LABELS[$i]}" "${SUITE_DIRS[$i]}"
done

echo
echo "=================== summary ==================="
printf '%s\n' ${RESULTS[@]+"${RESULTS[@]}"}
TOTAL=$((N_PASS + N_FAIL + N_SKIP))
TALLY="$N_PASS/$TOTAL suite(s) passed, $N_FAIL failed"
[[ $N_SKIP -eq 0 ]] || TALLY="$TALLY, $N_SKIP skipped (no tests selected)"
echo "$TALLY"
[[ $N_FAIL -eq 0 ]] || exit 1
if [[ $N_PASS -eq 0 ]]; then
  echo "run_tests: no suite ran any tests (the selection matched nothing)" >&2
  exit 1
fi
exit 0

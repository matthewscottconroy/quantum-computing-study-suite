#!/usr/bin/env bash
# setup.sh -- bootstrap the Quantum Computing Study Suite environment.
#
# Usage:
#   ./setup.sh              create .venv (if absent), install requirements.txt,
#                           then smoke-check the core imports and every app
#   ./setup.sh --dev        ... plus requirements-dev.txt (pytest, notebooks) and
#                           a Jupyter kernel: "quantum-study" for the default .venv,
#                           "quantum-study-<venv dir name>" for any other VENV_DIR
#                           (two venvs with the same directory name share that
#                           kernel; the most recent --dev run wins)
#   ./setup.sh --python P   build the venv with interpreter P (also: PYTHON=P)
#   ./setup.sh --help       show this text
#
# Environment overrides:
#   PYTHON=/path/to/python3.12    interpreter used to create the venv
#                                 (ignored, with a warning, when the venv exists)
#   VENV_DIR=/path/to/venv        where the venv lives (default: <repo>/.venv)
#
# Relative paths given to --python / PYTHON / VENV_DIR are taken from the
# directory you run setup.sh in, not from the repository root.
#
# Safe to re-run: an existing venv is reused, installs are no-ops when
# everything is already present, and the kernel spec is simply refreshed.

if [ -z "${BASH_VERSION:-}" ]; then
  echo "setup.sh must be run with bash:  bash setup.sh" >&2
  exit 1
fi
set -euo pipefail

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
if [[ -t 1 && -z "${NO_COLOR:-}" && "${TERM:-dumb}" != "dumb" ]]; then
  BOLD=$'\e[1m'; DIM=$'\e[2m'; RED=$'\e[31m'; GREEN=$'\e[32m'; YELLOW=$'\e[33m'; RESET=$'\e[0m'
else
  BOLD=""; DIM=""; RED=""; GREEN=""; YELLOW=""; RESET=""
fi
step() { printf '\n%s==> %s%s\n' "$BOLD" "$*" "$RESET"; }
note() { printf '    %s%s%s\n' "$DIM" "$*" "$RESET"; }
ok()   { printf '    %s[ok]%s %s\n' "$GREEN" "$RESET" "$*"; }
warn() { printf '    %s[!]%s %s\n' "$YELLOW" "$RESET" "$*" >&2; }
die()  { printf '\n%sERROR:%s %s\n' "$RED" "$RESET" "$*" >&2; exit 1; }

usage() {   # print this file's comment header (everything up to the first non-comment line)
  awk 'NR == 1 { next } !/^#/ { exit } { sub(/^# ?/, ""); print }' "${BASH_SOURCE[0]}"
}

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
DEV=0
PY_SRC="env"      # "env": PYTHON came from the environment; "arg": --python on the command line
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dev)       DEV=1 ;;
    --python)    shift; [[ $# -gt 0 ]] || die "--python requires a path"; PYTHON="$1"; PY_SRC="arg" ;;
    --python=*)  PYTHON="${1#--python=}"; [[ -n "$PYTHON" ]] || die "--python requires a path"; PY_SRC="arg" ;;
    -h|--help)   usage; exit 0 ;;
    *)           usage >&2; die "unknown argument: $1" ;;
  esac
  shift
done

CALLER_PWD="$(pwd -P 2>/dev/null || printf '%s' "$PWD")"   # where the user ran us from
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
VENV_DIR="${VENV_DIR:-$REPO_ROOT/.venv}"
case "$VENV_DIR" in
  /*) ;;
  *)  VENV_DIR="$CALLER_PWD/$VENV_DIR" ;;     # relative paths are relative to the caller
esac
# (VENV_DIR is canonicalised with pwd -P once the directory exists, in step 2.)

PY_GIVEN=""       # how the interpreter override was supplied, for messages
if [[ -n "${PYTHON:-}" ]]; then
  case "$PYTHON" in
    /*)  ;;                                   # absolute: nothing to do
    */*) # a relative *path* (contains a slash) must be anchored to the caller's directory
         # before we cd into the repo; a bare name (python3.12) is a PATH lookup and is fine as-is.
         py_dir="$(cd "$(dirname "$PYTHON")" 2>/dev/null && pwd -P)" \
           || py_dir="$CALLER_PWD/$(dirname "$PYTHON")"      # parent missing: keep an absolute
         PYTHON="$py_dir/$(basename "$PYTHON")" ;;           # spelling so the error names it
  esac
  if [[ "$PY_SRC" == "arg" ]]; then
    PY_GIVEN="--python $PYTHON"
  else
    PY_GIVEN="PYTHON=$PYTHON (environment variable)"
  fi
fi
cd "$REPO_ROOT"

[[ -f requirements.txt ]] || die "requirements.txt not found next to setup.sh ($REPO_ROOT)"

export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_NO_INPUT=1

# ---------------------------------------------------------------------------
# 1. Find a suitable Python (prefer 3.12+, require >= 3.11)
# ---------------------------------------------------------------------------
MIN_PY="3.11"
PREF_PY="3.12"

py_version() {   # prints "X.Y" for an interpreter, or nothing if it cannot run
  "$1" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || true
}

version_ge() {   # version_ge X.Y A.B  ->  true when X.Y >= A.B
  local a_maj="${1%%.*}" a_min="${1#*.}" b_maj="${2%%.*}" b_min="${2#*.}"
  (( a_maj > b_maj || (a_maj == b_maj && a_min >= b_min) ))
}

find_python() {
  local candidates=() c v fallback="" fallback_v=""
  CHECKED=()
  if [[ -n "${PYTHON:-}" ]]; then
    candidates=("$PYTHON")
  else
    candidates=(python3.14 python3.13 python3.12 python3 python3.11 python)
  fi
  for c in "${candidates[@]}"; do
    if ! command -v "$c" >/dev/null 2>&1; then
      CHECKED+=("$c (not found)")
      continue
    fi
    v="$(py_version "$c")"
    if [[ -z "$v" ]]; then
      CHECKED+=("$c (does not run)")
      continue
    fi
    CHECKED+=("$c ($v)")
    if version_ge "$v" "$PREF_PY"; then
      PY_BIN="$c"; PY_VER="$v"; return 0
    fi
    if [[ -z "$fallback" ]] && version_ge "$v" "$MIN_PY"; then
      fallback="$c"; fallback_v="$v"
    fi
  done
  if [[ -n "$fallback" ]]; then
    PY_BIN="$fallback"; PY_VER="$fallback_v"; return 0
  fi
  return 1
}

step "Locating Python (>= $MIN_PY required, $PREF_PY+ preferred)"
PY_BIN=""; PY_VER=""
if [[ -x "$VENV_DIR/bin/python" || -x "$VENV_DIR/Scripts/python.exe" ]]; then
  VENV_DIR="$(cd "$VENV_DIR" && pwd -P)"     # canonical now that we know it exists (messages below)
  note "existing virtual environment found at $VENV_DIR; its interpreter will be reused"
  if [[ -n "$PY_GIVEN" ]]; then
    warn "$PY_GIVEN is ignored: the existing venv is reused as-is (rm -rf \"$VENV_DIR\" to rebuild with it)"
  fi
elif ! find_python; then
  printf '    checked: %s\n' "${CHECKED[@]}" >&2
  die "No Python >= $MIN_PY was found. Install one (Fedora: sudo dnf install python3.12;
       Debian/Ubuntu: sudo apt install python3.12 python3.12-venv; macOS: brew install python@3.12)
       and re-run, or point at one explicitly:  PYTHON=/path/to/python3.12 ./setup.sh"
else
  ok "using $PY_BIN ($PY_VER) -> $(command -v "$PY_BIN")"
  if ! version_ge "$PY_VER" "$PREF_PY"; then
    warn "Python $PY_VER works, but $PREF_PY+ is recommended for the newest Qiskit/PyQt6 wheels."
  fi
fi

# ---------------------------------------------------------------------------
# 2. Create (or reuse) the virtual environment
# ---------------------------------------------------------------------------
step "Virtual environment: $VENV_DIR"
REUSED=0          # 1 when an existing venv is reused
BIN_SUB="bin"     # "bin" (POSIX layout) or "Scripts" (Windows layout)
if [[ -x "$VENV_DIR/bin/python" ]]; then
  REUSED=1
  note "already exists; reusing"
elif [[ -x "$VENV_DIR/Scripts/python.exe" ]]; then
  BIN_SUB="Scripts"
  REUSED=1
  note "already exists (Windows layout); reusing"
elif [[ -e "$VENV_DIR" && -n "$(ls -A "$VENV_DIR" 2>/dev/null)" ]]; then
  die "$VENV_DIR exists but is not a usable virtual environment.
       Remove it (rm -rf \"$VENV_DIR\") or choose another location with VENV_DIR=... ./setup.sh"
else
  PRE_EXISTED=0     # 1 when the user created an (empty) directory and pointed VENV_DIR at it
  if [[ -d "$VENV_DIR" ]]; then PRE_EXISTED=1; fi
  note "creating with $PY_BIN ($PY_VER) ..."
  if ! "$PY_BIN" -m venv "$VENV_DIR"; then
    # Do not leave a half-built venv behind: delete a directory we created, but only
    # empty out (never delete) one that existed before we started.
    if (( PRE_EXISTED )); then
      find "$VENV_DIR" -mindepth 1 -delete 2>/dev/null || true
    else
      rm -rf -- "$VENV_DIR"
    fi
    die "Could not create the virtual environment. On Debian/Ubuntu install the venv module
       (sudo apt install python${PY_VER}-venv) and re-run."
  fi
  [[ -x "$VENV_DIR/bin/python" ]] || BIN_SUB="Scripts"
  ok "created"
fi

# The directory exists now: canonicalise it (drops "./", "..", trailing "/", symlinked
# checkout paths) so the default-location test below and the next-steps text are exact.
VENV_DIR="$(cd "$VENV_DIR" && pwd -P)" || die "cannot enter $VENV_DIR"
BIN_DIR="$VENV_DIR/$BIN_SUB"
VENV_PY="$BIN_DIR/python"
[[ "$BIN_SUB" == "bin" ]] || VENV_PY="$BIN_DIR/python.exe"
DEFAULT_VENV=0    # 1 when the venv is the default <repo>/.venv (compared canonically, so a
                  # .venv that is itself a symlink to the real venv still counts as the default)
DEFAULT_CANON="$(cd "$REPO_ROOT/.venv" 2>/dev/null && pwd -P)" || DEFAULT_CANON="$REPO_ROOT/.venv"
[[ "$VENV_DIR" == "$DEFAULT_CANON" ]] && DEFAULT_VENV=1

# Jupyter kernel identity (--dev): the default venv owns "quantum-study"; any other VENV_DIR
# gets a name derived from its directory name so it does not overwrite the default kernelspec
# (venvs that share a directory name share the kernel -- see the header).
if (( DEFAULT_VENV )); then
  KERNEL_NAME="quantum-study"
  KERNEL_LABEL="Quantum Study (.venv)"
else
  venv_tag="$(basename "$VENV_DIR")"
  KERNEL_LABEL="Quantum Study ($venv_tag)"
  venv_tag="${venv_tag//[^A-Za-z0-9._-]/-}"                 # kernel names: [a-z0-9._-] only
  KERNEL_NAME="quantum-study-$(printf '%s' "$venv_tag" | tr '[:upper:]' '[:lower:]')"
fi

VENV_VER="$(py_version "$VENV_PY")"
[[ -n "$VENV_VER" ]] || die "The interpreter in $VENV_DIR does not run. Remove the directory and re-run."
if ! version_ge "$VENV_VER" "$MIN_PY"; then
  die "$VENV_DIR uses Python $VENV_VER, but >= $MIN_PY is required.
       Remove it (rm -rf \"$VENV_DIR\") and re-run so it is rebuilt with a newer interpreter."
fi
ok "python $VENV_VER at $VENV_PY"

if ! "$VENV_PY" -m pip --version >/dev/null 2>&1; then
  note "pip is missing from the venv; bootstrapping it with ensurepip ..."
  "$VENV_PY" -m ensurepip --upgrade >/dev/null \
    || die "pip could not be bootstrapped. Remove \"$VENV_DIR\" and re-run."
fi

# ---------------------------------------------------------------------------
# 3. Install dependencies
# ---------------------------------------------------------------------------
step "Upgrading pip"
# Not fatal: a re-run on an already-complete venv must still succeed with no network.
if ! "$VENV_PY" -m pip install --quiet --upgrade pip; then
  warn "pip could not be upgraded (offline, or PyPI unreachable?); continuing with the installed pip"
fi
ok "$("$VENV_PY" -m pip --version | cut -d' ' -f1-2)"

pip_install() {   # pip install "$@" -- silent when nothing needs installing, pip's normal
  # progress output otherwise (so a retry after an interrupted download is not mistaken for
  # a hang).  The dry run is offline-safe: --no-index makes it fail fast on anything missing.
  if "$VENV_PY" -m pip install --dry-run --no-index --quiet "$@" >/dev/null 2>&1; then
    note "already satisfied; nothing to install"
  else
    "$VENV_PY" -m pip install "$@"
  fi
}
PIP_HINT="pip could not complete the install (its output is above). Check the network/proxy
       and re-run: setup.sh picks up where it stopped."

step "Installing runtime dependencies (requirements.txt)"
(( REUSED )) || note "first run downloads PyQt6 + the Qiskit stack (a few hundred MB); later runs are quick"
pip_install -r requirements.txt || die "$PIP_HINT"
ok "runtime dependencies installed"

if (( DEV )); then
  step "Installing developer extras (requirements-dev.txt)"
  pip_install -r requirements-dev.txt || die "$PIP_HINT"
  ok "developer extras installed"

  step "Registering Jupyter kernel '$KERNEL_NAME'"
  "$VENV_PY" -m ipykernel install --user --name "$KERNEL_NAME" \
      --display-name "$KERNEL_LABEL"
  ok "kernel '$KERNEL_NAME' registered (pick '$KERNEL_LABEL' in Jupyter)"
fi

# ---------------------------------------------------------------------------
# 4. Smoke check (headless Qt)
# ---------------------------------------------------------------------------
step "Smoke check"
if ! QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg "$VENV_PY" - <<'PY'
import sys
print(f"    python      {sys.version.split()[0]}  ({sys.executable})")
from PyQt6 import QtCore, QtWidgets
app = QtWidgets.QApplication([])          # offscreen: proves the Qt platform plugin loads
print(f"    PyQt6       {QtCore.PYQT_VERSION_STR}  (Qt {QtCore.QT_VERSION_STR}, platform: {app.platformName()})")
import qiskit
print(f"    qiskit      {qiskit.__version__}")
try:
    import qiskit_aer
    print(f"    qiskit-aer  {qiskit_aer.__version__}")
except ImportError:
    print("    qiskit-aer  not importable (local simulators unavailable)")
import anthropic
print(f"    anthropic   {anthropic.__version__}")
PY
then
  die "Smoke check failed (traceback above). If PyQt6 failed to import on Linux, install the Qt
       system libraries: Debian/Ubuntu: sudo apt install libxcb-cursor0 libegl1 libgl1 libxkbcommon0
                         Fedora:        sudo dnf install xcb-util-cursor mesa-libEGL mesa-libGL libxkbcommon"
fi
ok "all core imports work"

# Every app, one interpreter per app (never import two apps in one process), the
# same check CI runs.  Importing main.py builds no windows and writes no study data.
step "Smoke check: importing every app (offscreen Qt, one subprocess each)"
APP_COUNT=0; APP_LIST=""
for main_py in */main.py; do
  [[ -f "$main_py" ]] || continue
  app="${main_py%/main.py}"
  if ! out="$(cd "$app" && QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg "$VENV_PY" -c 'import main' 2>&1)"; then
    printf '%s\n' "$out" >&2
    die "'import main' failed in $app/ (traceback above). If the other apps passed this is a bug in
       that app rather than in the environment; reproduce it with:  cd $app && python -c 'import main'"
  fi
  APP_COUNT=$((APP_COUNT + 1)); APP_LIST="$APP_LIST $app"
done
(( APP_COUNT > 0 )) || die "no <app>/main.py found under $REPO_ROOT -- is the checkout complete?"
ok "$APP_COUNT apps import cleanly:$APP_LIST"

# ---------------------------------------------------------------------------
# 5. Next steps
# ---------------------------------------------------------------------------
SETUP_CMD="./setup.sh"
[[ "$CALLER_PWD" == "$REPO_ROOT" ]] || SETUP_CMD="\"$REPO_ROOT/setup.sh\""
if (( DEFAULT_VENV )); then
  ACTIVATE="source .venv/$BIN_SUB/activate"
  RERUN="$SETUP_CMD"
else
  ACTIVATE="source \"$BIN_DIR/activate\""
  RERUN="VENV_DIR=\"$VENV_DIR\" $SETUP_CMD"
fi

printf '\n%sSetup complete%s in %ds.\n' "$BOLD" "$RESET" "$SECONDS"
cat <<EOT

Next steps
  1. Activate the environment (each new terminal):
       cd "$REPO_ROOT"
       $ACTIVATE

  2. Optional: a Claude API key unlocks dynamic question generation and
     free-form grading. Every app launches without one. Apps look for it as
       export ANTHROPIC_API_KEY=sk-ant-...                  (environment variable)
     or, to persist it without touching your shell config:
       mkdir -p ~/.config/quantum-study
       echo "sk-ant-..." > ~/.config/quantum-study/api_key.txt

  3. Take the 20-question placement diagnostic:
       python coach.py --diagnostic

  4. Launch an app:
       python launch.py
     (or run one directly, e.g.  cd flashcard-drill && python main.py)
EOT
if (( DEV )); then
  cat <<EOT
  5. Developer extras are installed:
       pytest                       (run inside any app directory)
       jupyter lab notebooks/       (choose the "$KERNEL_LABEL" kernel)
EOT
else
  printf '\n  Re-run with  %s --dev  to add pytest and the Jupyter notebook tooling.\n' "$RERUN"
fi
printf '\n  setup.sh is safe to re-run at any time.\n\n'

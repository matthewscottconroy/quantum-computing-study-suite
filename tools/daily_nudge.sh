#!/usr/bin/env bash
# tools/daily_nudge.sh — invite the user to today's plan.
#
# Runs `coach.py` with the repository venv and delivers the result two ways:
#
#   1. a desktop notification (notify-send) when a D-Bus session bus is
#      reachable — title "Quantum Study — today's plan", body = the
#      TODAY'S PLAN lines, normal urgency, an icon when one can be found;
#   2. the full plan on stdout, so cron mail / journald keeps a copy.
#
# Usage:
#   tools/daily_nudge.sh              # notify + print
#   tools/daily_nudge.sh --dry-run    # print only, never notify
#   tools/daily_nudge.sh --quiet      # notify only (prints if notifying fails)
#
# Environment:
#   QUANTUM_NUDGE_ICON        icon name or path to pass to notify-send
#   QUANTUM_STUDY_DATA_DIR    honoured by coach.py (history + coach state)
#
# Degradation (all exit 0, the plan still reaches stdout):
#   - notify-send not installed,
#   - no session bus (headless, ssh, a cron job with no logged-in session),
#   - notify-send itself failing.
# Exit 1 with a clear message when the venv or coach.py is missing, or when
# coach.py fails; exit 2 on a bad command line.
#
# The repository root is derived from this script's own location (symlinks
# resolved), so the script works from any cwd and from cron's bare
# environment.  bash 4+; GNU or BSD sed/awk/find.

set -uo pipefail

PROG="${0##*/}"

# --- locate the repository ------------------------------------------------
SELF="${BASH_SOURCE[0]}"
while [ -L "$SELF" ]; do
    _target="$(readlink "$SELF")"
    case "$_target" in
        /*) SELF="$_target" ;;
        *)  SELF="$(dirname "$SELF")/$_target" ;;
    esac
done
ROOT="$(cd "$(dirname "$SELF")/.." && pwd)"

VENV_PY="$ROOT/.venv/bin/python"
COACH="$ROOT/coach.py"

TITLE="Quantum Study — today's plan"
APP_NAME="Quantum Study"
PLAN_HEADER="TODAY'S PLAN"

warn() { printf '%s: %s\n' "$PROG" "$*" >&2; }
die()  { printf '%s: %s\n' "$PROG" "$*" >&2; exit 1; }

usage() {
    cat <<USAGE
Usage: $PROG [--dry-run | --quiet] [-h|--help]

  (no flags)  notify via notify-send and print the full plan to stdout
  --dry-run   print the plan only; never send a notification
  --quiet     send the notification only; print only if notifying failed
USAGE
}

DRY_RUN=0
QUIET=0
while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run) DRY_RUN=1 ;;
        --quiet|-q) QUIET=1 ;;
        -h|--help) usage; exit 0 ;;
        --) shift; break ;;
        *) printf '%s: unknown option: %s\n' "$PROG" "$1" >&2
           usage >&2
           exit 2 ;;
    esac
    shift
done
if [ "$DRY_RUN" -eq 1 ] && [ "$QUIET" -eq 1 ]; then
    printf '%s: --dry-run and --quiet are mutually exclusive\n' "$PROG" >&2
    exit 2
fi

# --- preconditions --------------------------------------------------------
if [ ! -x "$VENV_PY" ]; then
    die "no usable Python in the repo venv.
  expected: $VENV_PY
  create it with:
      python3 -m venv '$ROOT/.venv'
      '$ROOT/.venv/bin/pip' install -r '$ROOT/requirements.txt'
  (or run '$ROOT/setup.sh')"
fi
[ -f "$COACH" ] || die "coach.py not found at $COACH"

# --- session bus ----------------------------------------------------------
# cron and systemd --user timers start with a thin environment; a running
# user session still exposes its bus at $XDG_RUNTIME_DIR/bus, so adopt that
# when DBUS_SESSION_BUS_ADDRESS is unset.  No bus => no notification.
have_session_bus() {
    if [ -n "${DBUS_SESSION_BUS_ADDRESS:-}" ]; then
        return 0
    fi
    local runtime_dir="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
    if [ -S "$runtime_dir/bus" ]; then
        export XDG_RUNTIME_DIR="$runtime_dir"
        export DBUS_SESSION_BUS_ADDRESS="unix:path=$runtime_dir/bus"
        return 0
    fi
    return 1
}

# --- icon -----------------------------------------------------------------
# A repo asset wins; otherwise the first themed name actually present in an
# icon directory is used (notify-send resolves bare names through the theme).
# Prints nothing and returns 1 when no icon is available.
find_icon() {
    if [ -n "${QUANTUM_NUDGE_ICON:-}" ]; then
        printf '%s\n' "$QUANTUM_NUDGE_ICON"
        return 0
    fi
    local cand name dir hit
    for cand in "$ROOT/assets/icon.png" "$ROOT/assets/icon.svg" \
                "$ROOT/assets/quantum-study.png"; do
        if [ -f "$cand" ]; then
            printf '%s\n' "$cand"
            return 0
        fi
    done
    for name in quantum-study applications-science dialog-information; do
        for dir in "${XDG_DATA_HOME:-$HOME/.local/share}/icons" \
                   /usr/share/icons /usr/share/pixmaps; do
            [ -d "$dir" ] || continue
            hit="$(find "$dir" -type f \
                    \( -name "$name.png" -o -name "$name.svg" \
                       -o -name "$name.xpm" \) 2>/dev/null | head -n 1)"
            if [ -n "$hit" ]; then
                printf '%s\n' "$name"
                return 0
            fi
        done
    done
    return 1
}

# Notification bodies are parsed as markup by several daemons.
escape_markup() {
    printf '%s' "$1" | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g'
}

# --- run the coach --------------------------------------------------------
ERR_FILE="$(mktemp "${TMPDIR:-/tmp}/quantum-nudge.XXXXXX")" || die "mktemp failed"
trap 'rm -f "$ERR_FILE"' EXIT

RAW="$(cd "$ROOT" && NO_COLOR=1 TERM=dumb "$VENV_PY" coach.py 2>"$ERR_FILE")"
RC=$?
if [ "$RC" -ne 0 ]; then
    [ -s "$ERR_FILE" ] && cat "$ERR_FILE" >&2
    die "coach.py failed (exit $RC)"
fi
[ -s "$ERR_FILE" ] && cat "$ERR_FILE" >&2

# rich disables colour when stdout is a pipe, but strip CSI sequences anyway
# so a forced-colour environment can never leak escapes into a notification.
ESC=$'\033'
PLAN_TEXT="$(printf '%s\n' "$RAW" | sed -e "s/${ESC}\[[0-9;?]*[ -/]*[@-~]//g")"

# The notification body: the lines between "TODAY'S PLAN" and the blank line
# that closes the section, de-indented.
BODY="$(printf '%s\n' "$PLAN_TEXT" | awk -v hdr="$PLAN_HEADER" '
    !grab { if (index($0, hdr) == 1) grab = 1; next }
    /^[[:space:]]*$/ { exit }
    { sub(/^[[:space:]]+/, ""); print }
')"
if [ -z "$BODY" ]; then
    warn "no \"$PLAN_HEADER\" section in coach.py output — sending a short nudge"
    BODY="Your plan is ready — run: python coach.py"
fi

# --- deliver --------------------------------------------------------------
[ "$QUIET" -eq 1 ] || printf '%s\n' "$PLAN_TEXT"

NOTIFIED=0
if [ "$DRY_RUN" -eq 0 ]; then
    if ! command -v notify-send >/dev/null 2>&1; then
        warn "notify-send not found — desktop notification skipped"
    elif ! have_session_bus; then
        warn "no D-Bus session bus — desktop notification skipped"
    else
        NOTIFY_ARGS=(-u normal -a "$APP_NAME")
        if ICON="$(find_icon)" && [ -n "$ICON" ]; then
            NOTIFY_ARGS+=(-i "$ICON")
        fi
        if notify-send "${NOTIFY_ARGS[@]}" "$TITLE" "$(escape_markup "$BODY")"; then
            NOTIFIED=1
        else
            warn "notify-send failed (exit $?) — desktop notification skipped"
        fi
    fi
    if [ "$QUIET" -eq 1 ] && [ "$NOTIFIED" -eq 0 ]; then
        warn "falling back to stdout"
        printf '%s\n' "$PLAN_TEXT"
    fi
fi

exit 0

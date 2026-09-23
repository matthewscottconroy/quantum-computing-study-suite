#!/usr/bin/env bash
# tools/install_nudge.sh — schedule tools/daily_nudge.sh once a day.
#
# Prefers a systemd --user timer (survives reboots, logs to journald, catches
# up on a missed day with Persistent=true) and falls back to a crontab line
# when no user systemd manager is reachable.
#
# Usage:
#   tools/install_nudge.sh                  # install at 09:00
#   tools/install_nudge.sh --time 07:30     # install at 07:30
#   tools/install_nudge.sh --status         # what is scheduled right now
#   tools/install_nudge.sh --uninstall      # remove it again
#
# Flags:
#   --time HH:MM   daily run time (default 09:00)
#   --systemd      force the systemd --user timer backend
#   --cron         force the crontab backend
#   --dry-run      print what would be installed/removed; change nothing
#   --unit-dir DIR where the .service/.timer go
#                  (default ${XDG_CONFIG_HOME:-~/.config}/systemd/user)
#   --status, --uninstall, -h/--help
#
# Test hooks (also keep the installer safe to exercise):
#   DESTDIR                   prefix for the unit dir; when set, systemctl is
#                             never invoked (files are staged only)
#   QUANTUM_NUDGE_UNIT_DIR    same as --unit-dir
#   QUANTUM_NUDGE_CRONTAB     crontab command to use (default: crontab)
#   QUANTUM_NUDGE_SYSTEMCTL   systemctl command to use (default: systemctl)
#
# Installing is idempotent: unit files are rewritten in place and the crontab
# entry lives inside a marked block that is replaced, never duplicated.
# Exit 0 on success, 1 on failure, 2 on a bad command line.

set -uo pipefail

PROG="${0##*/}"

SELF="${BASH_SOURCE[0]}"
while [ -L "$SELF" ]; do
    _target="$(readlink "$SELF")"
    case "$_target" in
        /*) SELF="$_target" ;;
        *)  SELF="$(dirname "$SELF")/$_target" ;;
    esac
done
ROOT="$(cd "$(dirname "$SELF")/.." && pwd)"
NUDGE="$ROOT/tools/daily_nudge.sh"
INSTALLER="$(cd "$(dirname "$SELF")" && pwd)/$(basename "$SELF")"

UNIT_BASE="quantum-study-nudge"
SERVICE="$UNIT_BASE.service"
TIMER="$UNIT_BASE.timer"
BEGIN_MARK="# >>> $UNIT_BASE (tools/install_nudge.sh) >>>"
END_MARK="# <<< $UNIT_BASE <<<"

CRONTAB_CMD="${QUANTUM_NUDGE_CRONTAB:-crontab}"
SYSTEMCTL_CMD="${QUANTUM_NUDGE_SYSTEMCTL:-systemctl}"

warn() { printf '%s: %s\n' "$PROG" "$*" >&2; }
die()  { printf '%s: %s\n' "$PROG" "$*" >&2; exit 1; }

usage() {
    cat <<USAGE
$PROG — schedule tools/daily_nudge.sh once a day.

Prefers a systemd --user timer and falls back to a crontab line when no
user systemd manager is reachable.

Usage:
  $PROG                  # install at 09:00
  $PROG --time 07:30     # install at 07:30
  $PROG --status         # what is scheduled right now
  $PROG --uninstall      # remove it again

Flags:
  --time HH:MM    daily run time (default 09:00)
  --systemd       force the systemd --user timer backend
  --cron          force the crontab backend
  --dry-run, -n   print what would be installed/removed; change nothing
  --unit-dir DIR  where the .service/.timer go
                  (default \${XDG_CONFIG_HOME:-~/.config}/systemd/user)
  --status        show both backends
  --uninstall     remove the timer and/or the crontab block
  -h, --help      this text

Test hooks:
  DESTDIR                  prefix for the unit dir; systemctl is then never
                           invoked (unit files are staged only)
  QUANTUM_NUDGE_UNIT_DIR   same as --unit-dir
  QUANTUM_NUDGE_CRONTAB    crontab command to use (default: crontab)
  QUANTUM_NUDGE_SYSTEMCTL  systemctl command to use (default: systemctl)
USAGE
}

# --- command line ---------------------------------------------------------
TIME_SPEC="09:00"
BACKEND=""          # "", systemd, cron
ACTION="install"    # install | status | uninstall
DRY_RUN=0
DEFAULT_UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
UNIT_DIR="${QUANTUM_NUDGE_UNIT_DIR:-$DEFAULT_UNIT_DIR}"

while [ $# -gt 0 ]; do
    case "$1" in
        --time)
            [ $# -ge 2 ] || { warn "--time needs an HH:MM argument"; exit 2; }
            TIME_SPEC="$2"; shift ;;
        --time=*)    TIME_SPEC="${1#--time=}" ;;
        --unit-dir)
            [ $# -ge 2 ] || { warn "--unit-dir needs a directory"; exit 2; }
            UNIT_DIR="$2"; shift ;;
        --unit-dir=*) UNIT_DIR="${1#--unit-dir=}" ;;
        --systemd)   BACKEND="systemd" ;;
        --cron)      BACKEND="cron" ;;
        --dry-run|-n) DRY_RUN=1 ;;
        --status)    ACTION="status" ;;
        --uninstall) ACTION="uninstall" ;;
        -h|--help)   usage; exit 0 ;;
        *) warn "unknown option: $1"; usage >&2; exit 2 ;;
    esac
    shift
done

if [[ ! "$TIME_SPEC" =~ ^([0-9]|[01][0-9]|2[0-3]):[0-5][0-9]$ ]]; then
    warn "--time must be HH:MM in 24-hour form (got: $TIME_SPEC)"
    exit 2
fi
HH="${TIME_SPEC%%:*}"
MM="${TIME_SPEC##*:}"
HH_PAD="$(printf '%02d' "$((10#$HH))")"
MM_PAD="$(printf '%02d' "$((10#$MM))")"
CRON_HH="$((10#$HH))"
CRON_MM="$((10#$MM))"
TIME_PAD="$HH_PAD:$MM_PAD"

# DESTDIR (or any unit dir systemd does not read) stages the unit files
# somewhere harmless and keeps systemctl out of it -- that is what makes this
# installer safe to exercise in a test.
DESTDIR="${DESTDIR:-}"
UNIT_DIR_FULL="${DESTDIR%/}$UNIT_DIR"
STAGED=0
STAGED_WHY=""
if [ -n "$DESTDIR" ]; then
    STAGED=1
    STAGED_WHY="DESTDIR=$DESTDIR is set"
fi
if [ "$UNIT_DIR" != "$DEFAULT_UNIT_DIR" ]; then
    STAGED=1
    STAGED_WHY="${STAGED_WHY:+$STAGED_WHY; }the unit dir is not systemd's own ($DEFAULT_UNIT_DIR)"
fi

[ -f "$NUDGE" ] || die "tools/daily_nudge.sh not found at $NUDGE"
if [ ! -x "$NUDGE" ] && [ "$ACTION" = "install" ]; then
    warn "$NUDGE is not executable — scheduling it via 'bash' would still work,"
    warn "but run: chmod +x '$NUDGE'"
fi

# --- backend detection ----------------------------------------------------
systemd_available() {
    command -v "$SYSTEMCTL_CMD" >/dev/null 2>&1 || return 1
    "$SYSTEMCTL_CMD" --user show-environment >/dev/null 2>&1
}
cron_available() { command -v "$CRONTAB_CMD" >/dev/null 2>&1; }

pick_backend() {
    if [ -n "$BACKEND" ]; then
        printf '%s\n' "$BACKEND"
        return 0
    fi
    if systemd_available; then
        printf 'systemd\n'
    elif cron_available; then
        printf 'cron\n'
    else
        return 1
    fi
}

# --- rendering ------------------------------------------------------------
render_service() {
    cat <<UNIT
[Unit]
Description=Quantum Study — daily plan nudge
Documentation=file://$ROOT/tools/README.md

[Service]
Type=oneshot
WorkingDirectory=$ROOT
ExecStart=$NUDGE
UNIT
}

render_timer() {
    cat <<UNIT
[Unit]
Description=Quantum Study — daily plan nudge at $TIME_PAD

[Timer]
OnCalendar=*-*-* $TIME_PAD:00
Persistent=true
Unit=$SERVICE

[Install]
WantedBy=timers.target
UNIT
}

cron_line() { printf '%d %d * * * %s\n' "$CRON_MM" "$CRON_HH" "$NUDGE"; }

cron_block() {
    printf '%s\n' "$BEGIN_MARK"
    cron_line
    printf '%s\n' "$END_MARK"
}

read_crontab() { "$CRONTAB_CMD" -l 2>/dev/null; }

# existing crontab with our marked block removed
crontab_without_block() {
    read_crontab | awk -v b="$BEGIN_MARK" -v e="$END_MARK" '
        $0 == b { skip = 1; next }
        $0 == e { skip = 0; next }
        !skip   { print }
    '
}

crontab_has_block() {
    local content
    content="$(read_crontab)"
    case $'\n'"$content"$'\n' in
        *$'\n'"$BEGIN_MARK"$'\n'*) return 0 ;;
    esac
    return 1
}

crontab_mentions_nudge() {
    local content
    content="$(read_crontab)"
    [[ "$content" == *daily_nudge.sh* ]]
}

write_crontab() {   # stdin -> crontab
    "$CRONTAB_CMD" -
}

# --- install --------------------------------------------------------------
install_systemd() {
    local svc="$UNIT_DIR_FULL/$SERVICE" tmr="$UNIT_DIR_FULL/$TIMER"

    if [ "$DRY_RUN" -eq 1 ]; then
        printf 'DRY RUN — would write %s:\n\n' "$svc"
        render_service | sed -e 's/^\(.\)/    \1/'
        printf '\nDRY RUN — would write %s:\n\n' "$tmr"
        render_timer | sed -e 's/^\(.\)/    \1/'
        printf '\nDRY RUN — would then run:\n'
        printf '    %s --user daemon-reload\n' "$SYSTEMCTL_CMD"
        printf '    %s --user enable --now %s\n' "$SYSTEMCTL_CMD" "$TIMER"
        return 0
    fi

    mkdir -p "$UNIT_DIR_FULL" || die "cannot create $UNIT_DIR_FULL"
    render_service > "$svc" || die "cannot write $svc"
    render_timer   > "$tmr" || die "cannot write $tmr"

    local verb="Installed"
    if [ "$STAGED" -eq 1 ]; then
        verb="Staged"
        printf '%s — unit files written, systemctl not invoked.\n\n' \
            "$STAGED_WHY"
    else
        "$SYSTEMCTL_CMD" --user daemon-reload \
            || warn "systemctl --user daemon-reload failed"
        if ! "$SYSTEMCTL_CMD" --user enable --now "$TIMER"; then
            die "systemctl --user enable --now $TIMER failed"
        fi
    fi

    printf '%s a systemd --user timer:\n' "$verb"
    printf '  %s\n  %s\n' "$svc" "$tmr"
    printf '  runs %s every day at %s (Persistent=true catches up a missed day)\n' \
        "$NUDGE" "$TIME_PAD"
    printf '  output goes to the journal:  journalctl --user -u %s\n' "$SERVICE"
    printf '  next run:  %s --user list-timers %s\n' "$SYSTEMCTL_CMD" "$TIMER"
    printf '  run it now:  %s --user start %s\n' "$SYSTEMCTL_CMD" "$SERVICE"
    printf '\nRemove it with:\n  %s --uninstall\n' "$INSTALLER"
    printf '\nNote: without lingering the timer only runs while you are logged in;\n'
    printf '  enable it with:  loginctl enable-linger %s\n' "$(id -un)"
}

install_cron() {
    cron_available || die "no crontab command found ($CRONTAB_CMD)"
    local new
    new="$(crontab_without_block; cron_block)"

    if [ "$DRY_RUN" -eq 1 ]; then
        printf 'DRY RUN — would add this crontab block:\n\n'
        cron_block | sed -e 's/^\(.\)/    \1/'
        printf '\nDRY RUN — resulting crontab:\n\n'
        printf '%s\n' "$new" | sed -e 's/^\(.\)/    \1/'
        printf '\nDRY RUN — would install it with: %s -\n' "$CRONTAB_CMD"
        return 0
    fi

    printf '%s\n' "$new" | write_crontab || die "$CRONTAB_CMD - failed"

    printf 'Installed a crontab entry:\n\n'
    cron_block | sed -e 's/^/  /'
    printf '\n  runs every day at %s; cron mails stdout to you (MAILTO in the crontab)\n' \
        "$TIME_PAD"
    printf '\nRemove it with:\n  %s --uninstall\n' "$INSTALLER"
}

# --- uninstall ------------------------------------------------------------
uninstall_all() {
    local removed=0 kept svc="$UNIT_DIR_FULL/$SERVICE" tmr="$UNIT_DIR_FULL/$TIMER"

    if [ -f "$svc" ] || [ -f "$tmr" ]; then
        removed=1
        if [ "$DRY_RUN" -eq 1 ]; then
            printf 'DRY RUN — would run: %s --user disable --now %s\n' \
                "$SYSTEMCTL_CMD" "$TIMER"
            [ -f "$tmr" ] && printf 'DRY RUN — would remove %s\n' "$tmr"
            [ -f "$svc" ] && printf 'DRY RUN — would remove %s\n' "$svc"
        else
            if [ "$STAGED" -eq 0 ] && systemd_available; then
                "$SYSTEMCTL_CMD" --user disable --now "$TIMER" >/dev/null 2>&1
            fi
            rm -f "$tmr" "$svc"
            [ "$STAGED" -eq 0 ] && systemd_available \
                && "$SYSTEMCTL_CMD" --user daemon-reload >/dev/null 2>&1
            printf 'Removed the systemd --user timer (%s, %s).\n' "$TIMER" "$SERVICE"
        fi
    fi

    if cron_available && crontab_has_block; then
        removed=1
        if [ "$DRY_RUN" -eq 1 ]; then
            printf 'DRY RUN — would rewrite the crontab without the %s block.\n' \
                "$UNIT_BASE"
        else
            kept="$(crontab_without_block)"
            if [ -n "$kept" ]; then
                printf '%s\n' "$kept" | write_crontab \
                    || die "$CRONTAB_CMD - failed"
            else
                write_crontab </dev/null || die "$CRONTAB_CMD - failed"
            fi
            printf 'Removed the crontab entry (%s block).\n' "$UNIT_BASE"
        fi
    elif cron_available && crontab_mentions_nudge; then
        warn "the crontab mentions daily_nudge.sh outside the managed block —"
        warn "remove that line yourself with: $CRONTAB_CMD -e"
    fi

    if [ "$removed" -eq 0 ]; then
        printf 'Nothing to remove — no %s timer in %s and no managed crontab block.\n' \
            "$UNIT_BASE" "$UNIT_DIR_FULL"
    fi
}

# --- status ---------------------------------------------------------------
show_status() {
    local svc="$UNIT_DIR_FULL/$SERVICE" tmr="$UNIT_DIR_FULL/$TIMER" state

    printf 'daily nudge: %s\n' "$NUDGE"
    printf '\nsystemd --user timer (%s):\n' "$UNIT_DIR_FULL"
    if [ -f "$tmr" ]; then
        printf '  unit files present: %s, %s\n' "$TIMER" "$SERVICE"
        grep -E '^OnCalendar=' "$tmr" | sed -e 's/^/  /'
        if [ "$STAGED" -eq 0 ] && systemd_available; then
            state="$("$SYSTEMCTL_CMD" --user is-enabled "$TIMER" 2>&1)"
            printf '  is-enabled: %s\n' "$state"
            state="$("$SYSTEMCTL_CMD" --user is-active "$TIMER" 2>&1)"
            printf '  is-active:  %s\n' "$state"
            "$SYSTEMCTL_CMD" --user list-timers --no-pager "$TIMER" 2>/dev/null \
                | sed -e 's/^/  /'
        fi
    else
        printf '  not installed\n'
    fi

    printf '\ncrontab:\n'
    if ! cron_available; then
        printf '  no crontab command available (%s)\n' "$CRONTAB_CMD"
    elif crontab_has_block; then
        read_crontab | awk -v b="$BEGIN_MARK" -v e="$END_MARK" '
            $0 == b { show = 1 }
            show    { print "  " $0 }
            $0 == e { show = 0 }
        '
    else
        printf '  not installed\n'
    fi
}

# --- dispatch -------------------------------------------------------------
case "$ACTION" in
    status)    show_status ;;
    uninstall) uninstall_all ;;
    install)
        backend="$(pick_backend)" \
            || die "neither a systemd --user manager nor crontab is available"
        case "$backend" in
            systemd) install_systemd ;;
            cron)    install_cron ;;
            *)       die "unknown backend: $backend" ;;
        esac
        ;;
esac

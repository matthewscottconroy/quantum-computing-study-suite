#!/usr/bin/env bash
# tools/sync_history.sh — back up and sync the study history between machines.
#
# ~/.local/share/quantum-study/ is a flat directory of small JSON files: one
# history file per app, the coach state, the flashcard schedule.  It is the
# only thing in this project that cannot be regenerated, and it lives outside
# the study-suite repository on purpose (it is private, and it changes every
# time you study).  This script makes that directory a git repository *of its
# own* — not a submodule, never a subdirectory of the public repo — and syncs
# it to a private remote.
#
# Usage:
#   tools/sync_history.sh init [--remote URL]   # make it a repo, set the remote
#   tools/sync_history.sh push                  # commit everything and push
#   tools/sync_history.sh pull                  # fetch and merge
#   tools/sync_history.sh status                # where things stand
#   tools/sync_history.sh auto                  # pull then push (for cron)
#
# Flags (any subcommand):
#   --data-dir DIR   sync DIR instead of the default history directory
#                    (default: $QUANTUM_STUDY_DATA_DIR, else
#                     ~/.local/share/quantum-study — the same resolution
#                     coach.py, dashboard.py, launch.py and the apps use)
#   --dry-run, -n    print every command that would run; change nothing
#   --quiet, -q      only warnings and errors (cron-friendly)
#   -h, --help       this text
#
# Safety rules, enforced on every run:
#   - refuses outright if the data directory is inside the study-suite
#     repository, so study history can never be committed to the public repo
#     (a different enclosing checkout is a loud warning, not a refusal);
#   - never force-pushes, never rewrites history, never passes --force;
#   - never runs a mutating git command against the study-suite repository —
#     every write goes through `git -C "$DATA_DIR"`;
#   - every subcommand is idempotent and exits 0 when there is nothing to do;
#   - an unreachable remote is reported clearly and exits non-zero having
#     changed nothing: pull talks to the network before it touches the repo.
#
# Exit status: 0 success (including "nothing to do"), 1 failure,
#              2 bad command line, 3 merge conflict awaiting your decision.
#
# bash 4+, git 2.x.  No other dependencies.

set -uo pipefail

PROG="${0##*/}"

# Never inherit a git context: this may run from cron, or from a git hook in
# some other repository, both of which export these.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY
unset GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_PREFIX GIT_COMMON_DIR

# --- locate the study-suite repository (for the containment check) ---------
SELF="${BASH_SOURCE[0]}"
while [ -L "$SELF" ]; do
    _target="$(readlink "$SELF")"
    case "$_target" in
        /*) SELF="$_target" ;;
        *)  SELF="$(dirname "$SELF")/$_target" ;;
    esac
done
ROOT="$(cd "$(dirname "$SELF")/.." && pwd -P)"

DEFAULT_REMOTE="ssh://matthewscott@52.5.128.243/var/git/quantum-study-history.git"
REMOTE_NAME="origin"
DEFAULT_BRANCH="main"
MARKER="# quantum-study history — managed by tools/sync_history.sh"

DRY_RUN=0
QUIET=0
DATA_DIR=""
REMOTE_URL=""
REMOTE_GIVEN=0
CMD=""

# --- output helpers --------------------------------------------------------
say()  { [ "$QUIET" -eq 1 ] || printf '%s\n' "$*"; }
step() { [ "$QUIET" -eq 1 ] || printf '  %s\n' "$*"; }
warn() { printf '%s: %s\n' "$PROG" "$*" >&2; }
die()  { printf '%s: %s\n' "$PROG" "$*" >&2; exit 1; }

usage() {
    cat <<USAGE
$PROG — sync the quantum-study history directory to a private git remote.

Usage:
  $PROG init [--remote URL]   make the data dir a git repo, set the remote
  $PROG push                  commit everything (timestamped) and push
  $PROG pull                  fetch and merge the remote
  $PROG status                repo, remote, ahead/behind, uncommitted files
  $PROG auto                  pull then push — safe to run from cron

Flags:
  --data-dir DIR   directory to sync
                   (default: \$QUANTUM_STUDY_DATA_DIR, else
                    ~/.local/share/quantum-study)
  --remote URL     init only; default
                   $DEFAULT_REMOTE
  --dry-run, -n    print what would happen; change nothing
  --quiet, -q      warnings and errors only
  -h, --help       this text

The data directory becomes a git repository in its own right.  It is never a
submodule of the study suite and is never committed into the public repo —
$PROG refuses to run if the data dir sits inside this checkout.
Nothing here ever force-pushes.

On a second machine, clone instead of init:
  git clone <URL> ~/.local/share/quantum-study

Exit: 0 ok (including nothing to do), 1 failure, 2 usage, 3 merge conflict.
USAGE
}

# --- command line ----------------------------------------------------------
while [ $# -gt 0 ]; do
    case "$1" in
        init|push|pull|status|auto)
            if [ -n "$CMD" ]; then
                printf '%s: only one subcommand at a time (got "%s" and "%s")\n' \
                       "$PROG" "$CMD" "$1" >&2
                exit 2
            fi
            CMD="$1"
            ;;
        --data-dir)
            [ $# -ge 2 ] || { printf '%s: --data-dir needs a directory\n' "$PROG" >&2; exit 2; }
            DATA_DIR="$2"; shift
            ;;
        --data-dir=*) DATA_DIR="${1#--data-dir=}" ;;
        --remote)
            [ $# -ge 2 ] || { printf '%s: --remote needs a URL\n' "$PROG" >&2; exit 2; }
            REMOTE_URL="$2"; REMOTE_GIVEN=1; shift
            ;;
        --remote=*) REMOTE_URL="${1#--remote=}"; REMOTE_GIVEN=1 ;;
        --dry-run|-n) DRY_RUN=1 ;;
        --quiet|-q)   QUIET=1 ;;
        -h|--help)    usage; exit 0 ;;
        --) shift; break ;;
        *)
            printf '%s: unknown argument: %s\n' "$PROG" "$1" >&2
            usage >&2
            exit 2
            ;;
    esac
    shift
done

if [ -z "$CMD" ]; then
    printf '%s: no subcommand (expected init, push, pull, status or auto)\n' "$PROG" >&2
    usage >&2
    exit 2
fi
if [ "$REMOTE_GIVEN" -eq 1 ] && [ "$CMD" != "init" ]; then
    printf '%s: --remote only applies to "init"; change it later with\n' "$PROG" >&2
    printf '       git -C <data-dir> remote set-url %s <URL>\n' "$REMOTE_NAME" >&2
    exit 2
fi
[ -n "$REMOTE_URL" ] || REMOTE_URL="$DEFAULT_REMOTE"

# --- resolve the data directory -------------------------------------------
if [ -z "$DATA_DIR" ]; then
    DATA_DIR="${QUANTUM_STUDY_DATA_DIR:-$HOME/.local/share/quantum-study}"
fi
# A literal "~" arrived as text (e.g. --data-dir '~/x'), so expand it here.
# shellcheck disable=SC2088  # the tilde is data being matched, not a path
case "$DATA_DIR" in
    "~")   DATA_DIR="$HOME" ;;
    "~/"*) DATA_DIR="$HOME/${DATA_DIR#\~/}" ;;
esac
if [ -d "$DATA_DIR" ]; then
    DATA_DIR="$(cd "$DATA_DIR" && pwd -P)" || die "cannot enter data dir: $DATA_DIR"
else
    case "$DATA_DIR" in
        /*) ;;
        *)  DATA_DIR="$PWD/$DATA_DIR" ;;
    esac
fi

# --- ssh / git behaviour in a non-interactive context ----------------------
# Without this a cron run blocks forever on a passphrase or a host-key prompt
# instead of reporting "remote unreachable".
export GIT_TERMINAL_PROMPT="${GIT_TERMINAL_PROMPT:-0}"
if [ -z "${GIT_SSH_COMMAND:-}" ]; then
    if [ -t 0 ] && [ -t 2 ]; then
        GIT_SSH_COMMAND="ssh -o ConnectTimeout=15"
    else
        GIT_SSH_COMMAND="ssh -o ConnectTimeout=15 -o BatchMode=yes"
    fi
    export GIT_SSH_COMMAND
fi

# --- git plumbing ----------------------------------------------------------
# Every mutating command goes through g()/gq(), pinned to the data directory.
# The study-suite repo is only ever read, and only for the safety check.
g()  { git -C "$DATA_DIR" "$@"; }
gq() { git -C "$DATA_DIR" "$@" >/dev/null 2>&1; }

run() {
    if [ "$DRY_RUN" -eq 1 ]; then
        printf '  would run: %s\n' "$*"
        return 0
    fi
    "$@"
}

is_repo() { [ -e "$DATA_DIR/.git" ] && gq rev-parse --git-dir; }

# Physical toplevel of the repository containing $DATA_DIR, or "" if none.
enclosing_toplevel() {
    local dir top
    dir="$DATA_DIR"
    while [ ! -d "$dir" ] && [ "$dir" != "/" ] && [ "$dir" != "." ]; do
        dir="$(dirname "$dir")"
    done
    [ -d "$dir" ] || return 0
    top="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null)" || return 0
    [ -n "$top" ] || return 0
    (cd "$top" && pwd -P)
}

refuse_inside_suite() {
    printf '%s: refusing — the data dir is INSIDE the study-suite repository.\n' "$PROG" >&2
    printf '\n  data dir:    %s\n  study suite: %s\n\n' "$DATA_DIR" "$ROOT" >&2
    printf '  Study history is private and must never be committed to the public\n' >&2
    printf '  repo.  Keep it outside the checkout — every app, coach.py and\n' >&2
    printf '  dashboard.py follow QUANTUM_STUDY_DATA_DIR:\n\n' >&2
    printf '      mv %s ~/.local/share/quantum-study\n\n' "$DATA_DIR" >&2
    exit 1
}

# Hard refusal for the study suite; a loud warning for any other checkout.
assert_safe_location() {
    local top
    case "$DATA_DIR" in
        "$ROOT"|"$ROOT"/*) refuse_inside_suite ;;
    esac
    top="$(enclosing_toplevel)"
    [ -n "$top" ] || return 0
    [ "$top" != "$DATA_DIR" ] || return 0        # it is its own repo: fine
    [ "$top" != "$ROOT" ] || refuse_inside_suite
    warn "the data dir is inside another git repository ($top)."
    warn "make sure that repo ignores $DATA_DIR, or your study history will be committed to it."
}

current_branch() {
    local b
    b="$(g symbolic-ref --quiet --short HEAD 2>/dev/null)"
    if [ -n "$b" ]; then printf '%s\n' "$b"; else printf '%s\n' "$DEFAULT_BRANCH"; fi
}

remote_url() { g remote get-url "$REMOTE_NAME" 2>/dev/null; }
has_commits() { gq rev-parse --verify HEAD; }
# NB: `git rev-parse --git-path MERGE_HEAD` prints a path relative to the git
# command's cwd, not ours, so testing it with [ -f ] silently never matched.
# Ask git directly, and also catch a conflicted index whose MERGE_HEAD is gone.
merge_in_progress() {
    gq rev-parse --verify --quiet MERGE_HEAD && return 0
    [ -n "$(g ls-files --unmerged 2>/dev/null)" ]
}
dirty_files() { g status --porcelain --untracked-files=all 2>/dev/null; }

# Turn a remote URL into the one-liner that creates the bare repo behind it.
#
# The bare repo MUST be created with the branch this script pushes.  A plain
# `git init --bare` on a server whose init.defaultBranch is still "master"
# leaves HEAD pointing at a branch that never appears, and `git clone` of it
# checks out nothing ("remote HEAD refers to nonexistent ref") — which is
# exactly the second-machine path.  Hence -b.
create_remote_hint() {
    local url="$1" hostpart path port
    local init="git init --bare -b $DEFAULT_BRANCH"
    case "$url" in
        ssh://*)
            hostpart="${url#ssh://}"
            path="/${hostpart#*/}"
            hostpart="${hostpart%%/*}"
            case "$hostpart" in
                *:*) port="${hostpart##*:}"; hostpart="${hostpart%:*}"
                     printf "ssh -p %s %s '%s %s'\n" "$port" "$hostpart" "$init" "$path" ;;
                *)   printf "ssh %s '%s %s'\n" "$hostpart" "$init" "$path" ;;
            esac
            ;;
        file://*) printf "%s %s\n" "$init" "${url#file://}" ;;
        /*|./*|../*|~*) printf "%s %s\n" "$init" "$url" ;;
        *:*)  # scp-like  user@host:path
            hostpart="${url%%:*}"
            path="${url#*:}"
            printf "ssh %s '%s %s'\n" "$hostpart" "$init" "$path"
            ;;
        *) printf "%s %s\n" "$init" "$url" ;;
    esac
}

# Same command for a git older than 2.28, which has no `init -b`.
create_remote_hint_old_git() {
    local url="$1" hostpart path bare
    case "$url" in
        ssh://*)   hostpart="${url#ssh://}"; bare="/${hostpart#*/}"; hostpart="${hostpart%%/*}" ;;
        file://*)  hostpart=""; bare="${url#file://}" ;;
        /*|./*|../*|~*) hostpart=""; bare="$url" ;;
        *:*)       hostpart="${url%%:*}"; bare="${url#*:}" ;;
        *)         hostpart=""; bare="$url" ;;
    esac
    path="git init --bare $bare && git -C $bare symbolic-ref HEAD refs/heads/$DEFAULT_BRANCH"
    if [ -n "$hostpart" ]; then
        printf "ssh %s '%s'\n" "${hostpart%%:*}" "$path"
    else
        printf "%s\n" "$path"
    fi
}

# Classify a failed fetch/push.  $1 = captured output, $2 = the git operation
# ("fetch"/"push"), $3 = the subcommand to tell the user to re-run (default $2).
report_remote_failure() {
    local err="$1" what="$2" retry="${3:-$2}" url
    url="$(remote_url)"
    case "$err" in
        *"does not appear to be a git repository"*|*"Repository not found"*|\
        *"not a git repository"*|*"no such identity"*)
            warn "the host answered but there is no repository at that path."
            printf '\n  remote: %s\n\n  Create it once with:\n      %s\n\n' \
                   "${url:-<unset>}" "$(create_remote_hint "${url:-$DEFAULT_REMOTE}")" >&2
            ;;
        *"Could not resolve hostname"*|*"Connection refused"*|*"Connection timed out"*|\
        *"Network is unreachable"*|*"No route to host"*|*"Operation timed out"*|\
        *"Could not read from remote repository"*|*"Permission denied"*|\
        *"Host key verification failed"*|*"kex_exchange_identification"*|\
        *"unable to access"*)
            warn "cannot reach the history remote — nothing was uploaded or merged."
            printf '\n  remote: %s\n\n  git said:\n' "${url:-<unset>}" >&2
            printf '%s\n' "$err" | sed 's/^/      /' >&2
            printf '\n  Check the host is up and your key is loaded, then re-run:\n' >&2
            printf '      %s %s\n\n' "$PROG" "$retry" >&2
            ;;
        *"non-fast-forward"*|*"fetch first"*|*"rejected"*|*"behind its remote"*)
            warn "the remote has commits you do not have yet — nothing was pushed."
            printf '\n  Merge them first (this script never force-pushes):\n' >&2
            printf '      %s pull\n      %s push\n\n' "$PROG" "$PROG" >&2
            ;;
        *)
            warn "git $what failed:"
            printf '%s\n' "$err" | sed 's/^/      /' >&2
            printf '\n' >&2
            ;;
    esac
}

# --- shared preconditions --------------------------------------------------
require_dir() {
    [ -d "$DATA_DIR" ] || die "no such directory: $DATA_DIR
  Set it up once with:
      $PROG init"
}

require_repo() {
    require_dir
    is_repo || die "$DATA_DIR is not a git repository yet.
  Set it up once with:
      $PROG init"
}

require_no_merge() {
    if merge_in_progress; then
        printf '%s: a merge is still in progress in %s.\n' "$PROG" "$DATA_DIR" >&2
        printf '\n  Finish it before syncing again:\n' >&2
        printf '      git -C %s status          # see what conflicts\n' "$DATA_DIR" >&2
        printf '      git -C %s commit          # after resolving\n' "$DATA_DIR" >&2
        printf '      git -C %s merge --abort   # or back out entirely\n\n' "$DATA_DIR" >&2
        exit 3
    fi
}

require_remote() {
    [ -n "$(remote_url)" ] || die "no \"$REMOTE_NAME\" remote configured in $DATA_DIR.
  Set one with:
      $PROG init --remote <URL>"
}

# git needs an identity to commit.  Give the data repo its own if the user has
# no global one, so a cron sync never dies on "please tell me who you are".
ensure_identity() {
    gq -c user.useConfigOnly=true var GIT_COMMITTER_IDENT && return 0
    step "no git identity configured — setting a local one for this repo"
    g config user.name  "quantum-study sync" || return 1
    g config user.email "quantum-study@$(hostname -s 2>/dev/null || echo localhost)" || return 1
}

# Stage and commit everything.  Prints a note and returns 0 when the tree is
# already clean, so push and pull can both call it unconditionally.
commit_everything() {
    local changed count msg stat
    changed="$(dirty_files)"
    if [ -z "$changed" ]; then
        step "working tree clean — nothing to commit"
        return 0
    fi
    count="$(printf '%s\n' "$changed" | grep -c '^')"
    if [ "$DRY_RUN" -eq 1 ]; then
        printf '  would commit %s changed file(s):\n' "$count"
        printf '%s\n' "$changed" | sed 's/^/      /'
        return 0
    fi
    ensure_identity || return 1
    g add --all >/dev/null || { warn "git add failed in $DATA_DIR"; return 1; }
    if g diff --cached --quiet; then
        step "only ignored changes — nothing to commit"
        return 0
    fi
    local marked
    marked="$(g grep --cached -l -I -E '^(<<<<<<<|>>>>>>>) ' -- '*.json' 2>/dev/null)"
    if [ -n "$marked" ]; then
        warn "refusing to commit: these staged files still contain conflict markers."
        printf '%s\n' "$marked" | sed 's/^/      /' >&2
        printf '\n  Resolve them first, then re-run.  To unstage:\n' >&2
        printf '      git -C %s reset\n\n' "$DATA_DIR" >&2
        return 1
    fi
    msg="study history $(date '+%Y-%m-%d %H:%M:%S') on $(hostname -s 2>/dev/null || echo unknown)"
    stat="$(g diff --cached --stat=72 2>/dev/null | tail -n 20)"
    if ! printf '%s\n\n%s\n' "$msg" "$stat" | g commit --quiet --file=-; then
        warn "git commit failed in $DATA_DIR"
        return 1
    fi
    step "committed $count file(s): $msg"
    return 0
}

# --- subcommand: init ------------------------------------------------------
write_managed() {
    # $1 = filename, $2 = body already rendered
    local path="$DATA_DIR/$1"
    if [ -f "$path" ] && ! head -n 1 "$path" 2>/dev/null | grep -qF "$MARKER"; then
        step "$1 exists and was not written by this script — left alone"
        return 0
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
        printf '  would write %s\n' "$path"
        return 0
    fi
    printf '%s\n' "$2" >"$path" || { warn "could not write $path"; return 1; }
    step "wrote $1"
}

attributes_body() {
    cat <<ATTRS
$MARKER
#
# The study apps write small, indented JSON documents here.  Treat them as LF
# text so git diffs and merges them line by line on every platform.
* text=auto eol=lf

# JSON: line-wise diffs whose hunk headers name the enclosing key, so a
# history diff reads as \`@@ ... "sessions":\` instead of \`@@ -412,7 +412,9 @@\`.
# The "json" driver is just that hunk-header pattern; it is set in this repo's
# own config by \`sync_history.sh init\` (diff.json.xfuncname).
*.json  text eol=lf  diff=json

# Deliberately NOT merge=union.  A union merge concatenates both sides, which
# turns two valid JSON documents into one invalid one.  History files are
# append-mostly, so real conflicts are rare and worth a human decision —
# \`sync_history.sh pull\` prints exactly how to resolve them.
ATTRS
}

ignores_body() {
    cat <<IGNORES
$MARKER
#
# The apps write atomically: a temp file in this directory, then os.replace.
# A sync that catches one mid-write must not commit the half-written copy.
*.tmp
.*-*.json
*.swp
*~
.DS_Store
IGNORES
}

cmd_init() {
    assert_safe_location

    say "history sync — init"
    say "  data dir: $DATA_DIR"

    if [ ! -d "$DATA_DIR" ]; then
        step "creating $DATA_DIR"
        run mkdir -p "$DATA_DIR" || die "could not create $DATA_DIR"
    fi

    if is_repo; then
        step "already a git repository"
    elif [ "$DRY_RUN" -eq 1 ]; then
        printf '  would run: git -C %s init -b %s\n' "$DATA_DIR" "$DEFAULT_BRANCH"
    else
        g init --quiet -b "$DEFAULT_BRANCH" || die "git init failed in $DATA_DIR"
        step "git init -b $DEFAULT_BRANCH"
        # Re-check now that a .git exists: a symlinked data dir could still
        # have resolved inside another checkout.
        assert_safe_location
    fi

    write_managed .gitattributes "$(attributes_body)"
    write_managed .gitignore     "$(ignores_body)"

    if [ "$DRY_RUN" -eq 1 ]; then
        printf '  would run: git -C %s config diff.json.xfuncname <json key pattern>\n' "$DATA_DIR"
    elif is_repo; then
        g config diff.json.xfuncname '^[ \t]*"[A-Za-z0-9_.-]+"[ \t]*:' >/dev/null
        g config push.default simple >/dev/null
        # Nothing here force-pushes; also refuse a force-push *into* this repo.
        g config receive.denyNonFastForwards true >/dev/null
    fi

    local existing
    existing="$(remote_url)"
    # An existing remote is only replaced when --remote was passed explicitly;
    # the dry run has to say exactly that, not something more alarming.
    if [ -n "$existing" ] && [ "$REMOTE_GIVEN" -eq 0 ]; then
        REMOTE_URL="$existing"
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
        if [ "$existing" = "$REMOTE_URL" ]; then
            printf '  remote %s already set to %s (left alone)\n' "$REMOTE_NAME" "$REMOTE_URL"
        elif [ -n "$existing" ]; then
            printf '  would run: git -C %s remote set-url %s %s  (was %s)\n' \
                   "$DATA_DIR" "$REMOTE_NAME" "$REMOTE_URL" "$existing"
        else
            printf '  would run: git -C %s remote add %s %s\n' \
                   "$DATA_DIR" "$REMOTE_NAME" "$REMOTE_URL"
        fi
    elif [ -z "$existing" ]; then
        g remote add "$REMOTE_NAME" "$REMOTE_URL" || die "could not add remote"
        step "remote $REMOTE_NAME -> $REMOTE_URL"
    elif [ "$existing" != "$REMOTE_URL" ]; then
        g remote set-url "$REMOTE_NAME" "$REMOTE_URL" || die "could not set remote URL"
        step "remote $REMOTE_NAME -> $REMOTE_URL (was $existing)"
    else
        step "remote $REMOTE_NAME already set to $REMOTE_URL (left alone)"
    fi

    say ""
    say "The remote must exist as a bare repository.  Create it once with:"
    say ""
    say "    $(create_remote_hint "$REMOTE_URL")"
    say ""
    say "(git older than 2.28 has no \"init -b\"; there, use:"
    say "    $(create_remote_hint_old_git "$REMOTE_URL")"
    say ")"
    say ""
    say "Then:  $PROG push"
    return 0
}

# --- subcommand: push ------------------------------------------------------
cmd_push() {
    assert_safe_location
    require_repo
    require_no_merge
    require_remote

    local branch err rc upstream remote_head
    branch="$(current_branch)"
    say "history sync — push"
    say "  data dir: $DATA_DIR  (branch $branch -> $(remote_url))"

    commit_everything || return 1

    if [ "$DRY_RUN" -eq 1 ]; then
        printf '  would run: git -C %s push --set-upstream %s refs/heads/%s:refs/heads/%s\n' \
               "$DATA_DIR" "$REMOTE_NAME" "$branch" "$branch"
        return 0
    fi

    if ! has_commits; then
        step "no commits yet — nothing to push"
        return 0
    fi

    # Nothing to do?  Only believe the cached remote ref if the remote agrees.
    upstream="$(g rev-parse --verify --quiet "refs/remotes/$REMOTE_NAME/$branch")"
    if [ -n "$upstream" ] && [ "$upstream" = "$(g rev-parse HEAD)" ]; then
        remote_head="$(g ls-remote --heads "$REMOTE_NAME" "$branch" 2>/dev/null | awk 'NR==1{print $1}')"
        if [ -n "$remote_head" ] && [ "$remote_head" = "$upstream" ]; then
            step "remote already has $(g rev-parse --short HEAD) — nothing to push"
            return 0
        fi
    fi

    err="$(g push --set-upstream "$REMOTE_NAME" "refs/heads/$branch:refs/heads/$branch" 2>&1)"
    rc=$?
    if [ $rc -ne 0 ]; then
        report_remote_failure "$err" "push"
        has_commits && warn "your work IS committed locally ($(g rev-parse --short HEAD)); only the upload failed."
        return 1
    fi
    [ "$QUIET" -eq 1 ] || printf '%s\n' "$err" | sed '/^[[:space:]]*$/d;s/^/  /'
    step "pushed $branch ($(g rev-parse --short HEAD))"
    return 0
}

# --- subcommand: pull ------------------------------------------------------
print_conflict_help() {
    local conflicts="$1" f
    {
        printf '\n'
        printf '%s: merge conflict — the same history file changed on both machines.\n' "$PROG"
        printf '\n  Conflicting file(s) in %s:\n\n' "$DATA_DIR"
        while IFS= read -r f; do
            [ -n "$f" ] && printf '      %s\n' "$f"
        done <<<"$conflicts"
        printf '\n'
        printf '  History files are append-mostly: each machine added its own entries to\n'
        printf '  the same list, so "take both" is almost always the right answer.  Open\n'
        printf '  the file, keep BOTH sides of every <<<<<<< / ======= / >>>>>>> block,\n'
        printf '  and delete those three marker lines.  In JSON that usually leaves one\n'
        printf '  missing comma where the two sides meet — add it, then check it parses:\n\n'
        while IFS= read -r f; do
            [ -n "$f" ] || continue
            # shellcheck disable=SC2016  # $EDITOR is for the user's shell, not ours
            printf '      $EDITOR %s/%s\n' "$DATA_DIR" "$f"
            case "$f" in
                *.json) printf '      python3 -m json.tool %s/%s >/dev/null   # must parse\n' "$DATA_DIR" "$f" ;;
            esac
        done <<<"$conflicts"
        printf '\n      git -C %s add .\n' "$DATA_DIR"
        printf '      git -C %s commit --no-edit\n' "$DATA_DIR"
        printf '      %s push\n\n' "$PROG"
        printf '  To take one side wholesale instead:\n'
        printf '      git -C %s checkout --ours   <file>   # this machine\n' "$DATA_DIR"
        printf '      git -C %s checkout --theirs <file>   # the other machine\n\n' "$DATA_DIR"
        printf '  Or back out entirely and decide later:\n'
        printf '      git -C %s merge --abort\n\n' "$DATA_DIR"
    } >&2
}

cmd_pull() {
    assert_safe_location
    require_repo
    require_no_merge
    require_remote

    local branch err rc before after conflicts ref unrelated=0
    branch="$(current_branch)"
    ref="refs/remotes/$REMOTE_NAME/$branch"
    say "history sync — pull"
    say "  data dir: $DATA_DIR  (branch $branch <- $(remote_url))"

    if [ "$DRY_RUN" -eq 1 ]; then
        printf '  would run: git -C %s fetch %s\n' "$DATA_DIR" "$REMOTE_NAME"
        printf '  then, only if the fetch brought something new:\n'
        commit_everything || return 1
        printf '  would run: git -C %s merge --no-edit %s/%s\n' \
               "$DATA_DIR" "$REMOTE_NAME" "$branch"
        return 0
    fi

    # Network first, so an unreachable remote changes absolutely nothing.
    err="$(g fetch --quiet "$REMOTE_NAME" 2>&1)"
    rc=$?
    if [ $rc -ne 0 ]; then
        report_remote_failure "$err" "fetch" "pull"
        warn "your local history is untouched — nothing was staged, committed or merged."
        return 1
    fi

    if ! g rev-parse --verify --quiet "$ref" >/dev/null && ! has_commits; then
        # A clone of a bare repo whose HEAD was never set lands on an unborn
        # branch the remote has never heard of.  Adopt the remote's branch
        # rather than starting a second, parallel history.
        local alt
        alt="$(g for-each-ref --format='%(refname:lstrip=3)' "refs/remotes/$REMOTE_NAME/" \
               | grep -vx 'HEAD' | grep -x "$DEFAULT_BRANCH" | head -n 1)"
        [ -n "$alt" ] || alt="$(g for-each-ref --format='%(refname:lstrip=3)' \
               "refs/remotes/$REMOTE_NAME/" | grep -vx 'HEAD' | head -n 1)"
        if [ -n "$alt" ]; then
            step "local branch \"$branch\" is unborn and unknown to the remote — adopting \"$alt\""
            g symbolic-ref HEAD "refs/heads/$alt" || return 1
            branch="$alt"
            ref="refs/remotes/$REMOTE_NAME/$alt"
        fi
    fi
    if ! g rev-parse --verify --quiet "$ref" >/dev/null; then
        step "the remote has no \"$branch\" branch yet — nothing to merge"
        return 0
    fi

    # Nothing new upstream?  Leave the working tree completely alone.
    if has_commits && g merge-base --is-ancestor "$ref" HEAD; then
        step "already up to date ($(g rev-parse --short HEAD))"
        return 0
    fi

    # There is something to merge, so local edits have to be committed first:
    # merging into a dirty tree either refuses or mixes unsaved study data in.
    commit_everything || return 1

    if ! has_commits; then
        if ! g merge --quiet --no-edit --ff-only "$ref"; then
            warn "could not fast-forward the empty branch onto $REMOTE_NAME/$branch"
            return 1
        fi
        step "fast-forwarded to $(g rev-parse --short HEAD)"
        return 0
    fi

    if ! gq merge-base HEAD "$ref"; then
        unrelated=1
        step "this repo and the remote were initialised separately — joining the two histories"
    fi

    before="$(g rev-parse HEAD)"
    if [ "$unrelated" -eq 1 ]; then
        err="$(g merge --no-edit --allow-unrelated-histories "$ref" 2>&1)"
    else
        err="$(g merge --no-edit "$ref" 2>&1)"
    fi
    rc=$?
    if [ $rc -ne 0 ]; then
        conflicts="$(g diff --name-only --diff-filter=U 2>/dev/null)"
        if [ -n "$conflicts" ]; then
            print_conflict_help "$conflicts"
            return 3
        fi
        warn "merge failed:"
        printf '%s\n' "$err" | sed 's/^/      /' >&2
        return 1
    fi
    after="$(g rev-parse HEAD)"
    if [ "$before" = "$after" ]; then
        step "already up to date ($(g rev-parse --short HEAD))"
    else
        step "merged $REMOTE_NAME/$branch -> $(g rev-parse --short HEAD)"
        [ "$QUIET" -eq 1 ] || g diff --stat "$before" "$after" | sed 's/^/  /'
    fi
    return 0
}

# --- subcommand: status ----------------------------------------------------
cmd_status() {
    assert_safe_location

    printf 'history sync — status\n'
    printf '  data dir:    %s\n' "$DATA_DIR"

    if [ ! -d "$DATA_DIR" ]; then
        printf '  state:       does not exist yet\n'
        printf '  next:        %s init\n' "$PROG"
        return 0
    fi

    printf '  json files:  %s\n' \
        "$(find "$DATA_DIR" -maxdepth 1 -type f -name '*.json' 2>/dev/null | wc -l | tr -d ' ')"

    if ! is_repo; then
        printf '  state:       not a git repository\n'
        printf '  next:        %s init\n' "$PROG"
        return 0
    fi

    local branch url dirty n ref counts behind ahead
    branch="$(current_branch)"
    url="$(remote_url)"
    printf '  repo:        yes (branch %s)\n' "$branch"
    printf '  remote:      %s\n' "${url:-<none configured>}"

    if has_commits; then
        printf '  commits:     %s\n' "$(g rev-list --count HEAD 2>/dev/null)"
        printf '  last commit: %s\n' \
            "$(g log -1 --format='%h  %ad  %s' --date=format:'%Y-%m-%d %H:%M' 2>/dev/null)"
    else
        printf '  commits:     none yet\n'
    fi

    dirty="$(dirty_files)"
    if [ -z "$dirty" ]; then
        printf '  uncommitted: none\n'
    else
        n="$(printf '%s\n' "$dirty" | grep -c '^')"
        printf '  uncommitted: %s file(s)\n' "$n"
        printf '%s\n' "$dirty" | sed 's/^/      /'
    fi

    if merge_in_progress; then
        printf '  MERGE IN PROGRESS — resolve it before syncing again:\n'
        g diff --name-only --diff-filter=U 2>/dev/null | sed 's/^/      /'
    fi

    if [ -n "$url" ] && has_commits; then
        ref="refs/remotes/$REMOTE_NAME/$branch"
        if [ "$DRY_RUN" -eq 1 ]; then
            printf '  would run:   git -C %s fetch %s\n' "$DATA_DIR" "$REMOTE_NAME"
        elif ! gq fetch --quiet "$REMOTE_NAME"; then
            printf '  reachable:   NO (figures below are from the last successful fetch)\n'
        else
            printf '  reachable:   yes\n'
        fi
        if g rev-parse --verify --quiet "$ref" >/dev/null; then
            counts="$(g rev-list --left-right --count "$ref...HEAD" 2>/dev/null)"
            read -r behind ahead <<<"$counts"
            printf '  vs %s/%s: %s ahead, %s behind\n' \
                   "$REMOTE_NAME" "$branch" "${ahead:-?}" "${behind:-?}"
        else
            printf '  vs %s/%s: never synced (remote branch not seen yet)\n' \
                   "$REMOTE_NAME" "$branch"
        fi
    fi
    return 0
}

# --- subcommand: auto ------------------------------------------------------
cmd_auto() {
    local rc
    say "history sync — auto (pull, then push)"
    cmd_pull
    rc=$?
    if [ $rc -ne 0 ]; then
        if [ $rc -eq 3 ]; then
            warn "auto stopped at a merge conflict — NOT pushing a conflicted tree."
        else
            warn "auto stopped: the pull failed, so nothing was pushed."
        fi
        return $rc
    fi
    cmd_push
}

# --- dispatch --------------------------------------------------------------
case "$CMD" in
    init)   cmd_init ;;
    push)   cmd_push ;;
    pull)   cmd_pull ;;
    status) cmd_status ;;
    auto)   cmd_auto ;;
    *)      printf '%s: unknown subcommand: %s\n' "$PROG" "$CMD" >&2; exit 2 ;;
esac
exit $?

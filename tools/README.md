# tools/

## verify_docs.py

Regression checks for the study corpus (`docs/` and `lesson-plans/`). Run it
after editing corpus files; it exits `0` when everything passes and `1` with a
report when something broke.

```bash
python3 tools/verify_docs.py                 # all checks, incl. snippet execution
python3 tools/verify_docs.py --no-snippets   # static checks only (no venv needed)
python3 tools/verify_docs.py --structure     # one specific check
python3 tools/verify_docs.py --snippets -v   # run snippets, show passing blocks too
```

### Checks

| Flag | What it verifies |
|---|---|
| `--structure` | Every `docs/<chapter>/*.md` has `## Exercises` and `## Further Reading`; `<details>` tags are balanced and at least one per exercise item; every `<details>` block contains `<summary>Solution</summary>`; no empty sections; file is not truncated. |
| `--lint` | No AI self-talk leftovers ("wait, let…", "hmm,…", "let me recompute", …), no `TODO`/`FIXME`/`XXX ` markers, no stranded `·...` fragments (Pauli strings like `XXXX` are excluded). |
| `--crossrefs` | Markdown links and backtick paths that look like repo-relative `.md` file (or directory-link) references resolve to existing files. |
| `--readme` | `docs/README.md` file-map tables name files that exist in their chapter dirs (chapter files missing from a map are a warning, not a failure); `lesson-plans/README.md` lesson-table links resolve. |
| `--snippets` | Extracts the ` ```python ` blocks from `lesson-plans/06-qiskit.md`, `07-qasm.md`, and `10-transpiling.md` and executes them **cumulatively per file** (each block sees the namespace built by earlier blocks, matching how the lessons build context). Reports pass/skip/fail per block. |

Default (no flags) = all checks. `--no-snippets` drops the snippet run from
the default set. Warnings never affect the exit status.

### Snippet execution details

- **Requires the project venv**: blocks run under
  `.venv/bin/python` (the static checks need only system Python 3.14+, stdlib
  only). If the venv is missing, use `--no-snippets`.
- Blocks run in a **temporary working directory** (file-writing snippets never
  pollute the repo) with `MPLBACKEND=Agg` so matplotlib never opens windows.
- Blocks are **skipped automatically** with a note when they:
  - import `qiskit_ibm_runtime` or `pytket` (need external services/packages),
  - import any module not installed in the venv,
  - need an optional lazy dependency (e.g. `qiskit.qasm3.loads` needs
    `qiskit-qasm3-import`),
  - use names defined only in skipped blocks, or never defined by any prior
    block (lesson fragments that assume "your circuit").
- Manual skips: start a block with `# verify: skip — reason`, add an entry to
  `MANUAL_SKIPS` in the script, or pass `--skip 06-qiskit.md:3,5` at the CLI.
- `--timeout SEC` sets the per-block timeout (default 120 s).

To increase snippet coverage, install the optional packages in the venv:
`pip install qiskit-qasm3-import` (enables the OpenQASM 3 round-trip block in
`07-qasm.md`); `qiskit-ibm-runtime` would enable the fake-backend blocks.

<!-- ===================== Daily nudge ===================== -->

## Daily nudge — `daily_nudge.sh` + `install_nudge.sh`

`coach.py` builds a plan every day; these two scripts make sure you actually
see it. `daily_nudge.sh` delivers one day's plan, `install_nudge.sh` schedules
it.

### `daily_nudge.sh` — deliver today's plan

Runs `coach.py` with the repository venv and delivers the result two ways:

1. a **desktop notification** via `notify-send` — title
   `Quantum Study — today's plan`, body = the `TODAY'S PLAN` lines,
   normal urgency, an icon when one can be found;
2. the **full plan on stdout**, so cron mail and journald keep a copy.

```bash
tools/daily_nudge.sh              # notify + print
tools/daily_nudge.sh --dry-run    # print only, never notify
tools/daily_nudge.sh --quiet      # notify only
```

The repository root comes from the script's own location (symlinks resolved),
so it works from any working directory and from cron's bare environment.

| Situation | Behaviour |
|---|---|
| `notify-send` not installed | warns on stderr, prints the plan, **exit 0** |
| no D-Bus session bus | warns on stderr, prints the plan, **exit 0** |
| `notify-send` itself fails | warns on stderr, prints the plan, **exit 0** |
| `--quiet` and notifying failed | falls back to stdout so the plan is never lost |
| venv or `coach.py` missing | clear message naming the expected path, **exit 1** |
| `coach.py` fails | forwards its stderr, **exit 1** |
| bad flags (incl. `--dry-run --quiet`) | usage, **exit 2** |

Session bus: cron and systemd timers start with a thin environment, so when
`DBUS_SESSION_BUS_ADDRESS` is unset the script adopts `$XDG_RUNTIME_DIR/bus`
if that socket exists. No socket means no desktop session, so it just prints.

Environment: `QUANTUM_NUDGE_ICON` overrides the icon (a name or a path);
`QUANTUM_STUDY_DATA_DIR` is passed straight through to `coach.py`. Without an
override the icon is the first of `assets/icon.png`, `assets/icon.svg`,
`assets/quantum-study.png` that exists, else the first themed name among
`quantum-study`, `applications-science`, `dialog-information` actually present
in an icon directory, else no icon at all.

### `install_nudge.sh` — schedule it

Prefers a **systemd `--user` timer** (survives reboots, logs to journald, and
`Persistent=true` catches up a day the machine was off) and falls back to a
**crontab line** when no user systemd manager answers.

```bash
tools/install_nudge.sh                 # install at 09:00
tools/install_nudge.sh --time 07:30    # install at 07:30
tools/install_nudge.sh --status        # what is scheduled right now
tools/install_nudge.sh --uninstall     # remove it again
```

| Flag | Meaning |
|---|---|
| `--time HH:MM` | daily run time, 24-hour (default `09:00`) |
| `--systemd` / `--cron` | force a backend instead of auto-detecting |
| `--dry-run`, `-n` | print the unit files / crontab block; change nothing |
| `--unit-dir DIR` | where the units go (default `${XDG_CONFIG_HOME:-~/.config}/systemd/user`) |
| `--status` | report **both** backends, so a leftover cron line stays visible |
| `--uninstall` | remove the timer and/or the managed crontab block |

Installing is idempotent: the unit files are rewritten in place, and the
crontab entry lives between marker comments that are replaced rather than
duplicated, so re-running with a new `--time` retimes the job instead of
adding a second one. Every run prints what it installed and the exact command
that removes it.

What gets written:

```ini
# ~/.config/systemd/user/quantum-study-nudge.timer
[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true
Unit=quantum-study-nudge.service
```

```crontab
# >>> quantum-study-nudge (tools/install_nudge.sh) >>>
0 9 * * * /path/to/repo/tools/daily_nudge.sh
# <<< quantum-study-nudge <<<
```

With the systemd backend the plan goes to the journal
(`journalctl --user -u quantum-study-nudge.service`); with cron it is mailed
to you like any other cron output. A `--user` timer only fires while you are
logged in unless you run `loginctl enable-linger "$USER"` — the installer says
so after a systemd install.

### Testing the installer without installing anything

Two overrides keep the installer off your real systemd and crontab, which is
how its own verification is done:

- `--dry-run` prints the generated unit files or crontab block and stops.
- `DESTDIR=/tmp/stage` (or `--unit-dir /tmp/stage`) writes the unit files
  under that prefix and **skips `systemctl` entirely** — any unit directory
  that is not systemd's own puts the installer in this staged mode.
- `QUANTUM_NUDGE_CRONTAB=/path/to/fake-crontab` swaps the `crontab` command,
  and `QUANTUM_NUDGE_SYSTEMCTL` swaps `systemctl` (point it at a
  non-existent path to force the cron fallback).

```bash
tools/install_nudge.sh --systemd --dry-run --time 07:30   # show the units
tools/install_nudge.sh --cron    --dry-run                # show the cron line
DESTDIR=/tmp/stage tools/install_nudge.sh --systemd       # stage the units
```

Both scripts pass `bash -n` and `shellcheck -S style` cleanly.

## `export_cards.py` — take the flashcards off this desktop

The 550 flashcards live one-per-file under `flashcard-drill/cards/`, which is
great for review and terrible for drilling on a train. `export_cards.py` reads
that directory through flashcard-drill's own loader — the card text is never
duplicated anywhere — and re-emits the deck in three portable formats.

```bash
python3 tools/export_cards.py --all                 # all three -> exports/
python3 tools/export_cards.py --html --out _site    # just the web deck
python3 tools/export_cards.py --json --apkg         # no web deck
```

With no format flag, `--all` is assumed. `--out DIR` picks the output
directory (default `exports/`, which is gitignored); `-q` silences the
per-file report.

| Flag | Output | Needs |
|---|---|---|
| `--json` | `cards.json` — the whole deck as `{id, category, front, back}` objects, plus a count and the category list | stdlib |
| `--apkg` | `quantum-study.apkg` — an Anki package, one subdeck per category | `genanki` |
| `--html` | `index.html` — a self-contained offline web deck | stdlib |
| `--all`  | all three (the default) | `genanki` |

Only the Anki export needs a third-party package
(`pip install -r requirements-dev.txt` installs `genanki`). The JSON and HTML
paths are standard library only — no PyQt6, no qiskit — which is why the Pages
workflow builds the site with a bare Python and no `pip install`.

### `cards.json`

```json
{ "schema": "quantum-study/cards@1", "count": 550,
  "categories": ["Algorithms", "..."],
  "cards": [{ "id": "gate_CNOT", "category": "Gate Unitaries",
              "front": "...", "back": "..." }] }
```

Cards are sorted by category then id. Nothing else reads this file — it exists
so *you* can pipe the deck into whatever you like.

### `quantum-study.apkg` (Anki)

Import it into Anki (desktop or mobile) with **File → Import**. It creates
`Quantum Study` with one subdeck per category — `Quantum Study::Gate Unitaries`,
`Quantum Study::Pauli Matrices`, … — and tags every note `quantum-study` plus
its category (`Gate_Unitaries`, `States_and_Measurement`, …).

**Re-importing updates in place; it does not duplicate.** The deck ids, the
model id and every note GUID are derived from stable names (the note GUID *is*
the flashcard id), so after you edit a card under `flashcard-drill/cards/`,
re-export and re-import: Anki matches the GUIDs, rewrites those notes, and
leaves your review history alone. Never change `stable_id()`, `APKG_TIMESTAMP`
or the card ids themselves — that would orphan every note already in Anki and
the next import would land 550 duplicates.

Fields are HTML-escaped on the way in, so the `<`, `>` and `&` that appear in
card text (`⟨ψ|H|ψ⟩`, `A & B`) survive intact.

### `index.html` (offline web deck)

One file, ~168 KB, no CDN, no network requests of any kind: the cards, the
stylesheet and the script are all inlined. Open it from a phone, a USB stick
or a plane-mode laptop and it works. Built from the templates in
`tools/webdeck/`:

| File | Role |
|---|---|
| `tools/webdeck/index.html` | page skeleton; the exporter substitutes `/*{{DECK_CSS}}*/`, `/*{{DECK_JS}}*/`, `{{DECK_DATA}}`, `{{CARD_COUNT}}`, `{{CATEGORY_COUNT}}` |
| `tools/webdeck/deck.css` | mobile-first dark theme (same palette as `flashcard-drill/ui/theme.py`) |
| `tools/webdeck/deck.js` | queue building, reveal/rate, Leitner scheduling, localStorage |

Edit those three, never the generated `exports/index.html`. A missing
placeholder is a hard error, so the exporter cannot quietly ship a page with an
empty deck.

What it does: category filter with per-category due/new counts, shuffle,
tap-or-space to reveal, **Again / Good / Easy**, undo, and Leitner scheduling
(box intervals 0, 1, 2, 4, 8, 16, 32, 64, 128 days) saved to `localStorage`.
Keyboard shortcuts appear only on devices with a real keyboard:

| Key | Action |
|---|---|
| `space` / `enter` | reveal, then rate *Good* |
| `1` `2` `3` | Again / Good / Easy |
| `u` | undo the last rating |
| `s` | shuffle the rest of the session |
| `r` | rebuild the session queue |
| `f` | categories and settings |
| `?` / `esc` | shortcuts panel / close |

Progress is per-browser and never leaves the device. It is **separate from the
desktop app's history** — `~/.local/share/quantum-study/flashcard_history.json`
is untouched, and the web deck does not read it.

The category colours are read out of `flashcard-drill/ui/theme.py` by parsing
the `CATEGORY_COLORS` literal with `ast` (importing it would pull in PyQt6), so
a palette change on the desktop shows up in the web deck on the next export.

### Published to GitHub Pages

`.github/workflows/pages.yml` runs `export_cards.py --html --json` on every
push to `main` (and on manual dispatch) and deploys `_site/` to

<https://matthewscottconroy.github.io/quantum-computing-study-suite/>

with the raw deck alongside it at `/cards.json`. On a phone, use **Add to Home
Screen** — the page is self-contained, so once it is cached it keeps working
offline.

**Pages has to be switched on once, by hand:** repository **Settings → Pages →
Build and deployment → Source: GitHub Actions**. A workflow cannot enable
Pages for its own repository; until that is set, the deploy job fails with
*"Get Pages site failed"*. The build job installs nothing and takes seconds.

Before uploading, the workflow re-checks the artifact: the page must exist,
must carry exactly as many cards as there are card modules on disk, and must
not reference anything it would have to fetch over the network.

### Reproducibility

Every output is byte-for-byte identical across runs — no timestamps are
written, ids and GUIDs are derived from names, and the `.apkg` zip is repacked
with fixed entry metadata. `sha256sum exports/*` after two consecutive runs
gives the same three hashes, so a re-export is a no-op unless a card changed.

`export_cards.py` also refuses to export a short deck: `cards.all_cards()`
swallows per-module import errors, so the exporter compares the loaded count
against the number of card modules on disk and fails loudly if a card file is
broken, rather than shipping 549 cards.

<!-- ===================== Concept map ===================== -->

## `concept_map.py` + `concept_graph.json` — the corpus as a graph, not a ladder

Eighty-plus chapter files is past the point where "read chapter 3, then chapter
4" is useful navigation. `concept_graph.json` is a **curated prerequisite DAG**
over the corpus and `concept_map.py` scores it against your study history, so
the question it answers is the one you actually have: *given what I already
know, what am I ready to learn next?*

```bash
tools/concept_map.py                  # terminal view + "ready to learn next"
tools/concept_map.py --next 15        # a longer ready list (default 8)
tools/concept_map.py --area qec       # one area only
tools/concept_map.py --html           # exports/concept_map.html
tools/concept_map.py --dot | dot -Tsvg -o map.svg
tools/concept_map.py --check          # validate the graph against the repo
```

Stdlib only. It never writes to the study data directory — it only reads it,
through `dashboard.py`, and `QUANTUM_STUDY_DATA_DIR` is honoured because
dashboard honours it.

### `concept_graph.json` — the curated part

Nodes are **concepts, not files**. A concept names the corpus files that teach
it and the app categories that drill it, which is what makes mastery
computable:

```json
{ "id": "qpe", "label": "Quantum phase estimation", "area": "algo",
  "docs": ["docs/04_quantum_algorithms/04_quantum_phase_estimation.md"],
  "drills": [{ "app": "Flashcard Drill", "category": "Algorithms" },
             { "app": "Problem Trainer", "category": "Algorithms" },
             { "app": "Quantum Quiz",    "category": "Quantum Algorithm Design" }],
  "needs": ["qft", "eigen_spectral"] }
```

| Field | Meaning |
|---|---|
| `id` | stable snake_case key; `needs` lists refer to it |
| `label` | what the terminal view, the SVG and the DOT node print |
| `area` | one of the `areas[]` ids — a chapter group, used for grouping and DOT clusters |
| `docs` | repo-relative files that **teach** the concept (`docs/`, `lesson-plans/`, `labs/`, `projects/`) |
| `drills` | `{app, category}` pairs that **exercise** it; `app` is a `dashboard._FILES` key, `category` is that app's own vocabulary |
| `needs` | prerequisite concept ids — the edges. `A needs B` = B should be solid before A makes sense |

`mastery.threshold` / `mastery.min_evidence` / `mastery.seen_evidence` at the
top of the file are the band cut-offs (below). Edit those three numbers rather
than the code.

The node set covers every `docs/` chapter and every `lesson-plans/` lesson, at
roughly one to four concepts per chapter. **It is hand-curated on purpose** —
a graph derived from headings would be a table of contents, not a prerequisite
order. After any edit, run `--check`.

`category` uses each app's *own* vocabulary, which is not always what the
history file literally stores:

| App | `category` is | Why |
|---|---|---|
| Math Quiz / Quantum Quiz | the **subject** (`"Linear Algebra"`) | the history stores subject *and* topic; the graph works at subject level and `concept_map.py` folds each topic back to its subject via `<app>/core/topics.py` |
| Problem Trainer | the problem **topic** (`"Algorithms"`) | `problems_history.json` stores only `{problem_id, kind}`, so the id is mapped back to its topic via `problem-trainer/problems/**` |
| everything else | exactly what the history stores | flashcard/qec/vqa category, dojo & exam section, circuit-trainer `ProblemCategory` value |

Derivation attempts land in Problem Trainer's `"derivation"` bucket, which
carries no topic at all — seven different derivations share one label — so no
concept claims it and `--check` says so. That is the honest answer, not a bug.

### Mastery — dashboard's weighting, not a second copy of it

`concept_map.py` **imports** `dashboard.py`. Every graded encounter in every
app is flattened by `dashboard.iter_retention_events` and decayed by
`dashboard._session_weight` (14-day half-life). There is deliberately no second
history parser in the repo: the schemas are load-bearing.

For each concept, over the encounters in its drill categories:

- **score** = `Σ w·correct / Σ w·total` — decayed accuracy, 0–1
- **evidence** = `Σ w·total` — decayed count of graded items

| Band | Rule | Glyph |
|---|---|---|
| mastered | score ≥ `threshold` (0.80) **and** evidence ≥ `min_evidence` (5.0) | `●` |
| strong | score ≥ threshold but too few reps to trust it | `■` |
| learning | 0.5 ≤ score < threshold | `◆` |
| weak | score < 0.5 | `▼` |
| untouched | evidence < `seen_evidence` (0.5) | `·` |

Evidence is what stops one lucky answer from marking a concept mastered, and
the decay is what makes mastery expire: stop drilling a category and its
concepts slide back down on their own.

**Ready to learn next** = concepts that are *not* mastered but whose every
prerequisite *is*, ordered by how many concepts each one unlocks. With an empty
history that is exactly the graph's roots; as areas go green it walks forward.

### `--html` — one self-contained file

`exports/concept_map.html` (~210 KB, gitignored) is a layered left-to-right
drawing of the whole graph as **inline SVG**, generated server-side so it
renders with JavaScript off. No CDN, no fonts, no images, no `fetch` — nothing
it would have to go to the network for.

Hover a concept for its status, the files that teach it and the apps that drill
it; click to pin it and grey out everything that is not one of its
prerequisites or one of the things it unlocks; filter by name, area, docs path
or drill; drag to pan, wheel to zoom, **table view** for the same data as rows.
Light and dark are both selected, not auto-flipped.

Mastery is ordinal, so it is encoded **three ways at once** — colour, glyph and
written label — in the graph, the tooltip, the legend and the table. That is
deliberate: the status palette puts red beside green, which a deuteranope
cannot separate, so colour never carries the meaning alone.

### `--dot`

Graphviz `digraph`, one `cluster_*` subgraph per area, node fill and tooltip by
mastery band. Goes to stdout (or `--out FILE`), so
`tools/concept_map.py --dot | dot -Tsvg -o map.svg` gives a poster-sized
rendering with Graphviz's own layout.

### `--check` — the thing to run after editing the graph

| Check | Fails when |
|---|---|
| structure | an id is duplicated, a label or `docs` list is empty, `area` is unknown, `needs` has a duplicate or a self-loop, or a prerequisite id does not exist |
| acyclic | there is a prerequisite cycle — the offending path is printed |
| corpus refs | a `docs` path does not exist on disk |
| drills | `app` is not a dashboard app, or `category` is not in that app's real vocabulary (a case-only miss is reported with the correct spelling) |
| coverage | a `docs/` or `lesson-plans/` chapter is taught by no concept — **a warning by default**, a failure under `--strict` |

Coverage is only advisory by default on purpose: a chapter someone else just
added is a gap in the graph, not a broken reference, and it must not break this
check for everyone else. Run `--check --strict` when you are the one curating.

The app vocabularies are read **statically** out of the apps — card/problem/kata
modules are scanned for their `category=` / `section=` / `topic=` literals, and
`SECTIONS`, `SECTION_ORDER`, `TOPICS` and `ProblemCategory` are parsed with
`ast`, the same trick `export_cards.py` uses for the flashcard palette. The ten
app trees cannot be imported side by side (they all define a top-level `core`),
and nothing is duplicated into this tool.

Warnings never affect the exit status: `0` = clean, `1` = at least one failure.

<!-- ===================== History sync ===================== -->

## `sync_history.sh` — keep the study history across machines

`~/.local/share/quantum-study/` is the one thing in this project that cannot
be regenerated: every app's history file, `coach_state.json`, the flashcard
schedule. It is a flat directory of small JSON files, it lives outside this
repository on purpose (it is private, and it changes every time you study),
and until now it existed on exactly one disk.

`sync_history.sh` makes that directory **a git repository in its own right**
— not a submodule of the study suite, never a subdirectory of the public repo
— and syncs it to a private remote. Git is the right tool here because the
files are small, textual and append-mostly: you get the backup, the second
machine and the full "what did I know in March" history for free.

```bash
tools/sync_history.sh init      # once per machine
tools/sync_history.sh push      # commit everything and upload
tools/sync_history.sh pull      # fetch and merge
tools/sync_history.sh status    # where things stand
tools/sync_history.sh auto      # pull then push — for cron
```

### Subcommands

| Subcommand | What it does |
|---|---|
| `init [--remote URL]` | `git init -b main` the data dir if it is not a repo yet, write a managed `.gitattributes` and `.gitignore`, set the `diff.json` hunk-header driver, point `origin` at the remote, and print the exact one-line command that creates the bare repo on the server. |
| `push` | Stage everything, commit with a timestamped message (`study history 2026-09-23 09:40:41 on fedora`), push `main`. Never force. |
| `pull` | Fetch, and merge only if the fetch actually brought something. Local edits are committed first so the merge never mixes in unsaved study data. |
| `status` | Data dir, file count, branch, remote, whether the remote is reachable, ahead/behind, uncommitted files, and any merge left in progress. |
| `auto` | `pull` then `push`, stopping before the push if the pull failed. This is the cron entry point. |

### Flags

| Flag | Meaning |
|---|---|
| `--data-dir DIR` | sync `DIR` instead of the default. The default is `$QUANTUM_STUDY_DATA_DIR`, else `~/.local/share/quantum-study` — the same resolution `coach.py`, `dashboard.py`, `launch.py` and every app use. |
| `--remote URL` | `init` only. Default `ssh://matthewscott@52.5.128.243/var/git/quantum-study-history.git`. An existing `origin` is left alone unless you pass this. |
| `--dry-run`, `-n` | print every command that would run; change nothing, locally or remotely. |
| `--quiet`, `-q` | warnings and errors only. A successful `auto -q` prints nothing at all, which is what you want from cron. |

Exit status: `0` success (including "nothing to do"), `1` failure, `2` bad
command line, `3` a merge conflict waiting for your decision.

### First machine

```bash
tools/sync_history.sh init
# it prints, with your remote substituted:
ssh matthewscott@52.5.128.243 'git init --bare -b main /var/git/quantum-study-history.git'
tools/sync_history.sh push
```

The `-b main` matters. A plain `git init --bare` on a server whose
`init.defaultBranch` is still `master` leaves `HEAD` pointing at a branch that
never appears, and `git clone` of that repo checks out **nothing**. `init`
also prints the two-command form for a server git older than 2.28, which has
no `init -b`.

### Second machine — clone, do not init

```bash
git clone ssh://matthewscott@52.5.128.243/var/git/quantum-study-history.git \
          ~/.local/share/quantum-study
tools/sync_history.sh init      # adds the local-only bits: diff driver, remote check
tools/sync_history.sh auto
```

`init` on a second machine would start a *second* root commit, and the two
histories would then have to be joined. Cloning avoids that. (If it happens
anyway, `pull` detects the unrelated histories and joins them rather than
refusing; and if you cloned a bare repo with the dangling `HEAD` described
above, `pull` notices the unborn local branch and adopts the remote's.)

### Cron

`auto` is idempotent and silent on success, so it is safe on a timer:

```crontab
*/30 * * * * /path/to/repo/tools/sync_history.sh auto --quiet
```

Cron has no terminal, so the script sets `GIT_TERMINAL_PROMPT=0` and
`ssh -o BatchMode=yes -o ConnectTimeout=15` for itself when stdin/stderr are
not a tty. Without that a cron run blocks forever on a passphrase or a
host-key prompt instead of reporting "remote unreachable" and exiting.
Your key has to be available non-interactively (an agent, or a passphraseless
key for this one repo).

### Conflicts

Two machines appending to the same history file on the same day will
eventually collide. `pull` stops, exits `3`, and prints which file conflicted
plus the resolution that is almost always right:

```
sync_history.sh: merge conflict — the same history file changed on both machines.

  Conflicting file(s) in /home/you/.local/share/quantum-study:

      quiz_history.json

  History files are append-mostly: each machine added its own entries to
  the same list, so "take both" is almost always the right answer.  Open
  the file, keep BOTH sides of every <<<<<<< / ======= / >>>>>>> block,
  and delete those three marker lines.  In JSON that usually leaves one
  missing comma where the two sides meet — add it, then check it parses:
  ...
```

It then gives the literal `$EDITOR`, `python3 -m json.tool`, `git add`,
`git commit` and `checkout --ours/--theirs` commands with your paths already
filled in, and `merge --abort` to back out. Until you resolve it, `push`,
`pull` and `auto` all refuse with exit `3` rather than syncing a half-merged
tree.

### What `init` writes into the data dir

- **`.gitattributes`** — `* text=auto eol=lf` and `*.json diff=json`, so the
  JSON diffs line-wise with the enclosing key in the hunk header
  (`@@ -125,3 +125,3 @@ "score":`) instead of a bare line number. It
  deliberately does **not** set `merge=union`: a union merge concatenates both
  sides and turns two valid JSON documents into one invalid one.
- **`.gitignore`** — `*.tmp`, `.*-*.json` and friends. Every app writes
  atomically (temp file in the same directory, then `os.replace`), and a sync
  that catches one mid-write must not commit the half-written copy.
- **`diff.json.xfuncname`** in the repo's own `.git/config` — the hunk-header
  pattern the `diff=json` attribute refers to. It is repo-local, so run `init`
  once on each machine even after a clone.

Both files carry a marker comment on line 1. If you edit them, or write your
own, `init` sees the marker is gone and leaves them alone.

### Safety

- **Refuses to run at all if the data dir is inside this repository** — any
  subcommand, checked both by path and by `git rev-parse --show-toplevel`, so
  a symlink cannot sneak past it. Study history must never reach the public
  repo. A data dir inside some *other* checkout is a loud warning, not a
  refusal.
- **Never force-pushes**, never rewrites history, never passes `--force`;
  the push is an explicit `refs/heads/main:refs/heads/main` refspec.
- **Never touches the study-suite repo.** Every git write goes through a
  helper pinned to `git -C "$DATA_DIR"`. The single unpinned git call in the
  script is the read-only `rev-parse --show-toplevel` of the safety check.
  It also unsets `GIT_DIR`, `GIT_WORK_TREE` and friends on startup so it
  cannot inherit another repository's context from cron or a git hook.
- **Every subcommand is idempotent** and exits `0` when there is nothing to
  do — running `auto` every half hour costs one fetch.
- **An unreachable remote changes nothing.** `pull` talks to the network
  before it touches the repo, so a failed fetch leaves the tree exactly as it
  was. `push` commits locally first (your work is saved either way) and says
  so explicitly when only the upload failed.
- **Conflict markers can never be committed.** Beyond the merge-in-progress
  guard, a staged `*.json` containing `<<<<<<<` or `>>>>>>>` aborts the commit.

### Testing it without a server

Point it at a bare repo on the local disk — everything except the SSH hop is
identical:

```bash
git init --bare -b main /tmp/hist.git
tools/sync_history.sh init  --data-dir /tmp/A --remote /tmp/hist.git
tools/sync_history.sh push  --data-dir /tmp/A
git clone /tmp/hist.git /tmp/B
tools/sync_history.sh auto  --data-dir /tmp/B
```

`sync_history.sh` passes `bash -n` and `shellcheck -S style` cleanly.

---

## `gen_cloze.py` — cloze cards from the docs' Key Formulas

Every chapter under `docs/` closes with a **Key Formulas** section. That is a
large body of already-verified content that nothing turned into retrieval
practice, so `gen_cloze.py` reads those sections and blanks the right-hand side
of each identity:

```
FRONT  Grover operator:  G = ______
BACK   G = (2|s⟩⟨s| - I)(I - 2|x*⟩⟨x*|)  ·  Source: docs/04_quantum_algorithms/05_grover_search.md — Grover's Search Algorithm
```

The cards land one-per-file in `flashcard-drill/cards/cloze/` under the
category **Cloze**, in exactly the `Flashcard` shape the hand-written cards use,
so `cards.all_cards()`, the SM-2 scheduler, `export_cards.py` and the web deck
pick them up with no changes. The source chapter is always on the back, so a
missed card points straight at the reading.

```
python3 tools/gen_cloze.py                    # == --dry-run: report, write nothing
python3 tools/gen_cloze.py --write            # (re)generate the cards
python3 tools/gen_cloze.py --clean            # remove every generated card
python3 tools/gen_cloze.py --write --limit N  # cap the deck at the first N cards
python3 tools/gen_cloze.py --sample 20 --seed 7   # print a review sample
```

### Conservative by construction

A bad cloze is worse than no cloze, so every stage rejects rather than guesses.
A bug in this tool loses cards; it cannot ship a garbled one.

* **LaTeX → Unicode is a whitelist.** Chapters 01–04 write their formulas as
  `$$…$$`; chapters 05 onwards write them as Unicode in backticks. The
  converter maps each command the corpus actually uses and *raises* on anything
  else — an unknown macro, a `pmatrix`/`cases` environment, an alignment `&`, a
  surviving backslash or a stray brace — and the formula is dropped whole.
* **One card per entry, one relation per card.** The chosen clause must have a
  single kind of top-level relation. A chain of `=` is fine (the whole chain is
  the answer); `1/d ≤ Tr(ρ²) ≤ 1` and `P ≥ 4/π² ≈ 0.405` are dropped, because
  there is no single blank to fill.
* **The answer has to be recoverable from the prompt.** Dropped: ellipses
  (`…`), prose on the left-hand side, generic labels (`**Problem**:`), answers
  over 110 characters, an answer that is the prompt plus a decoration
  (`γ = γ†`), and any answer that already appears in the prompt.
* **Conditional and parenthetical formulas are dropped.** "Syndrome bit:
  `sᵢ = +1` **if** `E` commutes with `gᵢ`" would ask for a coin flip, because
  the condition lives in the prose outside the code span. So would an entry
  that gives two right-hand sides for one left-hand side (three jump operators
  all called `L`; the bit-flip and phase-flip `|0_L⟩`).
* **Duplicates are collapsed** across chapters: same left-hand side and answer,
  same left-hand side under the same label keywords, or two chapters stating one
  identity to different depths (`⟨M⟩ = ⟨ψ|M|ψ⟩` and
  `⟨M⟩ = ⟨ψ|M|ψ⟩ = Σ_m m p(m)`).

### Idempotence

A card's id is `cz_<chapter>_<file>_<label slug>_<hash>`, where the hash is over
*source path + label + left-hand side*. `--write` writes a file only when its
bytes change and deletes generated files that no longer correspond to a formula,
so two runs in a row leave the tree untouched (`unchanged: N`, nothing created,
updated or removed) and editing a chapter only rewrites that chapter's cards.
`--clean` removes the generated cards, the package `__init__.py` and the
directory, returning the deck to exactly its hand-written size.

### When the card count changes

Adding a chapter to `docs/` adds cards, which moves numbers that live outside
this tool. After a `--write` that changes the count, update:

* `flashcard-drill/tests/test_cards.py` — `EXPECTED_CARD_COUNT` and
  `EXPECTED_CATEGORY_COUNT` (15 with the Cloze category present).
* the card counts in `README.md`, `flashcard-drill/README.md`,
  `GETTING_STARTED.md`, `tools/README.md`, `launch.py` and `CONTRIBUTING.md`.
* `flashcard-drill/ui/theme.py` — `CATEGORY_COLORS` needs a `"Cloze"` entry, or
  the category falls back to the accent colour in the app and to
  `FALLBACK_COLOR` (`#58a6ff`, already used by Qiskit API) in the web deck.

`export_cards.py` needs no change: it reads the deck through
`cards.all_cards()` and compares the count against the modules on disk.

---

## `export_audio.py` — the audio deck

The desktop app needs a screen and the web deck needs a thumb. Neither reaches
the walk to the station. `export_audio.py` reads the same 856 cards through
flashcard-drill's own loader (`cards.all_cards()` — the card text is never
duplicated here either), rewrites each side from mathematical notation into
spoken English, and synthesises **front → silent recall gap → back** with
whatever offline speech engine this machine happens to have.

```bash
python3 tools/export_audio.py --dry-run --limit 60     # review the speech, synthesise nothing
python3 tools/export_audio.py --list-engines           # what this machine can do
python3 tools/export_audio.py                          # whole deck -> exports/audio/
python3 tools/export_audio.py --category "Pauli Matrices" --pause 6
python3 tools/export_audio.py --encode mp3 --out ~/audio-deck
python3 tools/export_audio.py --per-card --category Theorems
```

| Flag | Meaning |
|---|---|
| `--category NAME` | one category, repeatable, case-insensitive |
| `--limit N` | at most N cards, spread evenly across the chosen categories |
| `--pause SECONDS` | the recall gap between front and back (default 4) |
| `--voice NAME` | engine voice: `en-us`/`en-gb` for eSpeak, a `.onnx` path for piper |
| `--rate WPM` | speaking rate (default 150) |
| `--out DIR` | output directory (default `exports/audio/`, which is gitignored) |
| `--dry-run` | print raw and spoken text side by side; synthesise nothing |
| `--playlist` / `--no-playlist` | write `quantum-study.m3u` (default: yes) |
| `--per-card` | one file per card instead of one track per category |
| `--encode wav\|mp3\|opus` | re-encode with ffmpeg (default `wav`, needs nothing) |
| `--engine NAME` | force an engine instead of the best installed one |
| `--list-engines` | print the engine survey and exit |

### Output

By default you get **one continuous track per category**, numbered so a phone
sorts them in category order, plus two chapter sidecars and a playlist:

```
exports/audio/
  01-algorithms.wav            the track
  01-algorithms.cue            chapter marks, one per card (CUE sheet)
  01-algorithms.chapters.txt   the same marks as ffmetadata
  02-cloze.wav  02-cloze.cue  02-cloze.chapters.txt
  …
  quantum-study.m3u            #EXTM3U playlist over all the tracks
```

The `.cue` sheet is what most desktop and Android players read to give you
card-by-card skip inside a track. The ffmetadata file is for muxing an
audiobook:

```bash
ffmpeg -i 01-algorithms.wav -i 01-algorithms.chapters.txt \
       -map_metadata 1 -c:a aac 01-algorithms.m4b
```

`--per-card` swaps that for `exports/audio/<category>/0001-<card id>.wav`, with
the M3U naming every card. Skip-track then means skip-card, at the cost of 856
files.

**Sizes.** eSpeak returns 22.05 kHz mono 16-bit, so WAV runs about 2.7 MB per
minute — the whole deck is roughly 4.4 hours and 700 MB. `--encode mp3` drops
that to about 0.33 MB per minute (~90 MB for the deck); `--encode opus` is
smaller again. Both shell out to `ffmpeg`, and the tool checks for it *before*
it starts synthesising.

### Engines — offline only, no API key, no network

Surveyed in quality order; the first one installed wins, `--engine` overrides.

| Engine | Get it | Notes |
|---|---|---|
| `piper` | <https://github.com/rhasspy/piper> | neural, by far the most listenable; needs a voice model (`--voice en_US-*.onnx` or `PIPER_VOICE`) |
| `say` | built in to macOS | |
| `pico2wave` | `apt install libttspico-utils` / `dnf install svox-pico-tts` | small and natural; ignores `--rate` |
| `espeak-ng` | `apt install espeak-ng` / `dnf install espeak-ng` | robotic but clear, fast, and the only one that is everywhere |
| `espeak` | `apt install espeak` | the older eSpeak |
| `flite` | `apt install flite` | CMU Flite |
| `pyttsx3` | `pip install pyttsx3` | optional, imported lazily, and on Linux it only drives espeak — last resort |

Nothing here opens a socket. If no engine is installed the tool prints the
table above with the install lines, exits **3**, and writes nothing at all —
it will not silently degrade to a cloud voice, because there is no cloud path
in the file. `--dry-run` works with no engine installed, which is the point:
the speech text is reviewable on a machine that cannot speak.

`pyttsx3` is deliberately **not** in `requirements.txt` or
`requirements-dev.txt`. Everything else the tool needs is the standard library,
so `python3 tools/export_audio.py` works in a bare checkout.

### The pronunciation layer — the part that actually matters

Card text is written to be read. Fed to a synthesiser raw, `XZ = −iY` comes out
"ex-zed equals why", `⟨ψ|P_m|ψ⟩` comes out "psi pee em psi", and `O(√N)` and
`[[7,1,3]]` mostly come out as silence. So every card goes through thirteen
rewriting passes before synthesis:

| Raw | Spoken |
|---|---|
| `Σ_i \|i⟩⟨i\| = I` | the sum over i of ket i bra i equals I |
| `⟨ψ\|P_m\|ψ⟩` | bra psi, P sub m, ket psi |
| `⟨u\|v⟩ = Σ_{i=1}^n u_i^* v_i` | the inner product of u with v equals the sum from i equals 1 to n of u sub i conjugate v sub i |
| `Rx(θ) = e^{-iθX/2}` | R x theta equals e to the power of minus i theta X over 2 |
| `[CNOT, I⊗Z] = 0` | the commutator of CNOT and I tensor Z equals 0 |
| `{X, Z} = 0` | the anticommutator of X and Z equals 0 |
| `O(log(N)·κ²·ε⁻¹)` | big O of, log N times kappa squared times epsilon inverse |
| `Steane [[7,1,3]] code` | Steane the 7, 1, 3 code |
| `qc.count_ops()` | Q C dot count ops |
| `SparsePauliOp`, `SamplerV2` | Sparse Pauli Op, Sampler V two |
| `‖ρ−σ‖₁` | the trace norm of rho minus sigma |
| `â\|α⟩ = α\|α⟩` | a hat ket alpha equals alpha ket alpha |
| `Πₐ` vs `Π_{k=0}^{n-1}` | projector sub a — vs — the product from k equals 0 to n minus 1 of |

The mapping lives in plain tables at the top of the file — `GREEK`, `SYMBOLS`,
`SUPERSCRIPT`, `SUBSCRIPT`, `EXPONENT_WORDS`, `COMBINING`, `PRECOMPOSED`,
`PHRASES`, `WORD_PHRASES`, `SPOKEN_WORDS`, `FUNCTIONS` — followed by the passes
that use them, in the order `spoken()` documents. Add a row, re-run
`--dry-run`, read the sentence out loud.

Two tables are less obvious than the rest:

* **`SPOKEN_WORDS`** only fixes what the synthesiser gets *wrong*. eSpeak reads
  `LOCC` as "lock", `GHZ` as "gigahertz", `POVM` as "povvum", `EPR` as "epper"
  and `eigenstate` as "eye-jen-state", so those are respelled. It reads `BQP`,
  `QFT`, `CSS`, `HHL` and `CNOT` ("see-not") correctly already, so those are
  deliberately absent. Acronyms that *are* said as words stay words: `NISQ`
  → "nisk", `QASM` → "kazm", `SIC` → "sick", `CLOPS` → "clops".
* **Gate runs** — `XZX`, `HZH`, `IXZZX`, `SX` — are split into letters by rule
  rather than by table, because a run of `I X Y Z H S T` is always a product of
  gates. The handful that spell English words (`IT`, `HIS`, `THIS`, …) are
  excluded in `GATE_RUN_SKIP`.

`--dry-run` ends with an **unmapped characters** line listing anything the
tables did not recognise and the final scrub had to drop. That list is the
to-do list; it is empty for the current 856-card deck. Grouping brackets are
excluded from it, since they are dropped on purpose.

### Reviewing it

```bash
python3 tools/export_audio.py --dry-run --limit 60 | less
```

`--limit` spreads its budget across categories rather than taking the first N
cards, so `--limit 60` is four cards from each of the fifteen categories rather
than sixty cards of `Algorithms`. Each card prints the raw front, the spoken
front, the raw back and the spoken back, so a bad rewrite is visible without
listening to anything.

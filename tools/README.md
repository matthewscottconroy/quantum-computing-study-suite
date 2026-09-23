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

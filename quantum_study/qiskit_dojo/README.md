# Qiskit Dojo

A desktop "coding dojo" for the IBM Certified Quantum Developer exam
(C1000-179): you **write real Qiskit 2.x code** in an editor, the app
executes it in an isolated subprocess, and assertion-based tests grade it
automatically — fully offline.

Part of the quantum-study suite. Everything cross-cutting — the data
directory, the mistake journal, the confidence log, the flag store, the
palette and the Reference browser — comes from the repository's shared
[`common/`](../common/README.md) package rather than from a copy in this
tree; see *Shared code* below.

## Running

```bash
# From this directory (qiskit-dojo/), using the shared study venv:
../.venv/bin/python main.py        # or: python main.py inside the venv

# Or from the repo root:
.venv/bin/python qiskit-dojo/main.py
```

Tests (offscreen Qt, temp data dir — never touches your real history):

```bash
cd qiskit-dojo && ../.venv/bin/python -m pytest          # fast suite, a few seconds
../.venv/bin/python -m pytest -m slow tests/test_sweep.py  # all 72 katas through the harness
../.venv/bin/python -m pytest -m slow tests/test_sweep.py -k "dbg or mod"  # fix-it katas only
```

The fast suite checks the bank structurally (`tests/test_katas.py`: at least
72 katas, per-section floors matching the exam blueprint, unique ids and
titles, 2-3 hints, code compiles, files live in their section directory),
the persistence contracts (`tests/test_persistence.py`,
`tests/test_flagging.py`, `tests/test_mistake_journal.py`), the screens
offscreen (`tests/test_screens.py`, `tests/test_feedback_ui.py` — the
fail → reveal → categorise → pass loop end to end), schema versioning and
the errata button (`tests/test_schema_and_errata.py`) and the wiring to the
shared package (`tests/test_common_integration.py`).
The slow sweep runs every kata twice through `core/runner.py` - the
reference solution must pass and the starter must not - so it is one
parametrised case per kata (144+ cases, ~1-1.5 s each on an idle machine;
several minutes on a loaded one).

Dependencies: see `requirements.txt` (PyQt6, anthropic, matplotlib for the
UI). The **execution harness** additionally needs qiskit, qiskit-aer, and
numpy — these come from the shared venv at `../.venv`, which the harness
locates automatically (current venv → `../.venv/bin/python` → fallback to
`sys.executable`).

## What a session looks like

1. **Setup** — pick sections, kata count, and order (shuffled or
   curriculum order). Katas you have failed recently are weighted to
   reappear. The per-section pass rates shown here refresh every time
   you return to this screen.
2. **Kata** — task statement on the left; code editor (monospace,
   Tab = 4 spaces) and output pane on the right. Buttons:
   - **Run** — executes your code + the kata's tests in a subprocess
     (20 s timeout, `MPLBACKEND=Agg`), shows pass/fail plus stdout and
     tracebacks. Skip and End Session are disabled until the run
     finishes, so a result always lands on the kata it graded.
   - **Hint** — progressive hints (2–3 per kata).
   - **Reveal Solution** — shows the reference solution.
   - **Claude Review** — optional: sends the task + your code to Claude
     for style/idiom feedback. Needs an Anthropic API key
     (`ANTHROPIC_API_KEY` env var or `~/.config/quantum-study/api_key.txt`);
     everything else works with no key and no network.
   - **⚑ Flag for review** — toggles the current kata on the shared review
     list (`dojo_flagged.json`, see Persistence). Click again to unflag.
     The button shows the saved state whenever a kata opens, so a kata
     flagged in an earlier session lights up immediately.
   - **Confidence strip** — *"How sure are you this passes?"*, four
     buttons (1 Guessing … 4 Certain) above the output pane, asked
     **before** your first Run so the rating can never be hindsight. It
     is optional; **Don't ask again** turns it off for good. See
     *Confidence calibration* below.
   - **⚠ Report a problem** — the kata itself is wrong? One click opens a
     GitHub issue that is already filled in with the kata id, the prompt as
     you saw it, what you say is wrong, an optional correction and a
     severity. See *Reporting a bad kata* below.
   - **✎ What went wrong?** — appears under the output pane when you
     reveal the solution on a kata you could not pass. See *Mistake
     journal* below.
3. **Summary** — pass rate and per-section breakdown.
4. **History** — lifetime stats, per-section pass-rate charts, the
   **Mistake journal** card (open mistakes by cause, plus your confidence
   calibration and how often you were confidently wrong), and the
   **Flagged for review** list (section badge, title, date flagged) with a
   per-row **Unflag** button.
5. **Reference** — the **Browse Reference** button on the setup screen opens
   the in-app docs browser (see below); **← Back** returns to setup.

## Reference browser

The Reference screen is the suite's shared one — `common/ui/reference.py`,
one implementation for all ten apps instead of ten forks of the same ~900
lines. This app supplies exactly two things, as constructor arguments in
`ui/main_window.py` (both defined in `config.py`):

```python
ReferenceScreen(default_chapter=DOCS_DEFAULT_CHAPTER,   # 03_quantum_gates_and_circuits
                category_docs=DOCS_FOR_SECTION)         # kata section -> chapter
```

- **`DOCS_DEFAULT_CHAPTER`** — the dojo opens on
  `docs/03_quantum_gates_and_circuits/`, its own rung of the ladder; the
  whole corpus is still listed.
- **`DOCS_FOR_SECTION`** — one chapter per kata section, behind a
  **Jump to topic** picker in the top bar: *Sampler* → quantum
  measurements, *Estimator* → VQE fundamentals, *Results analysis* →
  probability and statistics, *Debugging* → tensor products and
  multipartite systems, and so on. `tests/test_screens.py` fails if a
  section is added to `katas/` without a chapter, or if a chapter is
  renamed out from under the map.

The docs root is resolved **at call time** (package location → cwd →
`sys.argv[0]`), so the app finds `<repo>/docs` from any working directory;
`QUANTUM_STUDY_DOCS_DIR` overrides it. Everything the old local screen did
still works — the chapter list, the live filter, Markdown rendering with
tables and fenced code, relative `.md` links, `#fragment` heading links,
`http(s)` links to the system browser, **Open externally** — plus what came
with the shared version: full-text search, a chapter filter, `$$…$$`
display-math rendering, resolved bare cross-references, and a **Show
solutions** checkbox that hides `<details>` exercise answers so you can try
them first.

Fully offline; nothing here touches the network or the API key.

## Sections (72 katas)

The 8 C1000-179 exam areas, weighted like the exam blueprint, plus two
dojo-specific practice styles:

| Section            | Katas | Notes |
|--------------------|-------|-------|
| Create circuits    | 10    | Bell/GHZ, registers (incl. cross-register Toffoli), Parameter/ParameterVector sweeps, compose, `to_gate` + control, dynamic `if_test`, inverse/uncompute, W state |
| Quantum operations | 9     | Operator identities, SparsePauliOp (little-endian) and Hamiltonian simplification, Statevector evolve, global phase vs equality, partial_trace/purity/fidelity, commuting groups, random_clifford |
| Run circuits       | 8     | AerSimulator run and one-job batches, generate_preset_pass_manager/ISA compliance, optimization level vs depth, Target queries, lowest-error qubit chain |
| Sampler            | 7     | SamplerV2 PUBs, parameterized and multi-PUB jobs, named- and two-creg BitArrays, post-selection, parameter broadcasting/PUB shape |
| Estimator          | 7     | EstimatorV2 PUBs, parameter sweeps, Hamiltonian energies, estimate vs exact diagonalisation, precision/shots/stds, observable broadcasting |
| Visualization      | 6     | plot_histogram (one and two datasets), plot_bloch_multivector, plot_state_city, `draw()` return types, `idle_wires`/`fold`/`cregbundle` |
| Results analysis   | 6     | per-qubit probabilities (endianness), ⟨ZZ⟩ and ⟨Z2 Z0⟩ from counts, marginal_counts, BitArray basics, shot-noise error bars |
| OpenQASM           | 3     | qasm2 round-trip, qasm3 loads/dumps, qasm3 round-trip that preserves the unitary |
| Debugging          | 8     | starter contains a REAL bug you must find and fix |
| Modernization      | 8     | starter uses retired 0.x APIs you must rewrite for 2.x |

Debugging bugs: wrong bit order, `enumerate()` reading a counts key
big-endian, measured circuit passed to the Estimator, observable not mapped
to the transpiled layout, non-ISA circuit submitted to a backend,
off-by-one in a parameter loop, wrong measurement basis, mutating `qc.data`
while iterating.

Modernization targets: `qiskit.execute`, `from qiskit import Aer`,
`BasicAer`, V1 primitives (`quasi_dists`), `bind_parameters`, `qc.qasm()`,
`CXCancellation`, and a full `execute` + V1-Sampler script that has to
become a preset pass manager + SamplerV2. Their tests fail on the legacy
starter and pass on a correct 2.x rewrite.

## Kata file format

One file per kata under `katas/<section_dir>/`, auto-discovered at
startup. Each file exposes a `KATA` object:

```python
from core.models import Kata

KATA = Kata(
    id="my_kata",                  # unique, stable (used in history)
    section="Sampler",             # must match a section name
    title="Short imperative title",
    difficulty="intermediate",     # beginner | intermediate | advanced
    prompt="Task statement…",      # markdown-ish plain text
    starter_code="…",              # what the editor opens with
    test_code="…",                 # plain asserts w/ helpful messages;
                                   # runs in the SAME namespace as the
                                   # user's code (their variables are in scope)
    solution_code="…",             # reference solution; must pass test_code
    hints=["…", "…"],              # 2–3 progressive hints
)
```

### Adding a kata

1. Drop a new file in the right `katas/` subdirectory (create a new
   directory for a new section and add it to `SECTION_ORDER` in
   `katas/__init__.py`).
2. Write `test_code` as bare asserts with actionable messages — the
   harness reports the first failing assert to the user.
3. Verify: the `solution_code` must pass, and the `starter_code` must not
   (for Debugging/Modernization katas it must fail with a test failure or
   an error in the user's code - never a timeout). Quick check from the
   app dir:

```python
import sys; sys.path.insert(0, ".")
from katas import all_katas
from core.runner import run_kata
k = next(k for k in all_katas() if k.id == "my_kata")
print(run_kata(k.solution_code, k.test_code))
```

   Then run the fast suite (it will tell you if the file failed to import,
   sits in the wrong directory, or has the wrong number of hints) and the
   sweep for just your kata:
   `../.venv/bin/python -m pytest -m slow tests/test_sweep.py -k my_kata`.
   Section floors live in `tests/test_katas.py::SECTION_TARGETS`; raise
   the floor when a section grows and you want the new count locked in.

## Execution harness (core/runner.py)

- Writes `user_code.py`, `test_code.py`, and a generated `harness.py`
  into a `tempfile.TemporaryDirectory`.
- Runs `<venv python> harness.py` with `cwd=` that temp dir,
  `MPLBACKEND=Agg`, and a 20-second timeout.
- The harness `exec`s the user code into a fresh namespace, then `exec`s
  the kata's `test_code` against that same namespace; a sentinel line on
  stdout plus exit code 0 marks success. Exit code 2 = error in user
  code, 3 = test failure/error.
- Feedback starts with a one-liner — `FAILED: <assert message>` or
  `ERROR: <ExceptionType>: <message>` — followed by a traceback with the
  harness's own frames removed, so the first frame you read is in
  `your_code.py` or `kata_tests.py` (with the offending source line).
- The UI runs the harness on a `QThread` so the window never blocks.

## Shared code (`common/`)

This app used to carry its own copy of the journal, the flag store, the
data-directory resolver, the palette, a loading overlay and a ~420-line
Reference screen. All six now come from `common/` at the repository root —
one implementation, ten callers, and a cross-cutting fix is one edit
instead of ten.

| Was here | Now |
|---|---|
| `persistence.py`'s journal internals (lock, merge, atomic write, caps) | `common.journal`, `common.locking`, `common.jsonio` |
| `persistence.py`'s `dojo_flagged.json` reader/writer | `common.flags` |
| `config.py`'s `QUANTUM_STUDY_DATA_DIR` handling | `common.datadir` (resolved per call, never frozen at import) |
| `ui/theme.py`'s palette and stylesheet | `common.ui.theme` |
| `ui/screens/reference_screen.py` (deleted) | `common.ui.reference` |
| `ui/widgets/loading_overlay.py` (deleted, was unused) | `common.ui.widgets.LoadingOverlay` |
| — | `common.schema` (versioning + backups), `common.ui.errata_dialog` |

### The import shim

The apps are not packages and several define the same top-level module
names, so the repository root is not importable from inside one.
`common_path.py` is an **unedited copy** of `common/app_shim.py`; importing
it appends `<repo>` to `sys.path` (appends, so this app's `tests`, `config`
and `ui` always win over the root's). Every module that touches `common`
imports it first — `config.py`, `persistence.py`, `ui/theme.py`,
`ui/main_window.py`, `ui/screens/kata_screen.py` and `tests/conftest.py` —
because each of them is, somewhere, the first thing imported:
`persistence.py` is loaded **by path** by the root suite's
`tests/test_journal_concurrency.py`, with no `main` and no `conftest` in
the way. `tests/test_common_integration.py` fails if a module forgets, or
if `common_path.py` drifts from the canonical copy.

### Where this app deliberately differs, and why

Two behaviours the shared journal does not have are kept here as thin
adapters over `common.journal`'s own primitives (its lock, its loaders, its
`save_*`), never as forked logic:

1. **A repeat failure folds into the kata's open row.**
   `journal.log_mistake` appends every miss — right for a quiz, where three
   misses of one card are three real signals. A dojo is not a quiz: you
   press Run while you iterate and the screen re-journals on every failed
   run, so appending would turn one stuck kata into thirty rows and drown
   `coach --mistakes`. `persistence.log_mistake` therefore takes
   `journal.lock`, re-reads with `journal.load_mistakes`, refreshes the open
   row and writes with `journal.save_mistakes` — so the locking, the
   foreign-row preservation, the growth cap, the version stamp and the
   backup are all the shared ones.
2. **A confidence rating is clamped, not rejected.**
   `journal.log_confidence` records nothing outside 1–4, meaning "the strip
   was skipped". This app decides that upstream (the kata screen only logs
   when the strip was used) and its documented contract is that
   `log_confidence` returns the row it stored, so it builds the row with the
   shared pure builder — which clamps — and appends it with
   `journal.save_confidence`.

One thing is local because it is *vocabulary*, not logic: the cause button
labels. The taxonomy written to disk is `common.journal.MISTAKE_CAUSES`
unchanged; only the wording is this app's, because "Confused two APIs" is
the dojo's failure mode and would mean nothing in math-quiz. Likewise
`ui/theme.py` keeps `SECTION_COLORS` and the handful of rules only a code
dojo needs (monospaced code/output panes, a horizontal scrollbar, splitter
and radio chrome) and appends them to the shared stylesheet with
`theme.extend()`.

### What changed for you

- The **focus ring** on buttons is now the suite's (a 2px accent border with
  compensating padding, so nothing shifts) rather than this app's 1px one,
  and `#pill` rules arrived from the shared base.
- `dojo_flagged.json` is written **atomically under a lock** and rebuilt
  from the *raw* list, so a row this app does not understand survives a
  rewrite instead of being deleted. A legacy bare-id list (`["id", "id"]`,
  which three other apps still write and `coach.py` parses) is now read as
  flags and upgraded to the object form on the first write.
- The growth cap trims **only this app's rows**. The old code sorted the
  whole merged file by timestamp and kept the newest *N*, which deleted
  other apps' rows during our own write — a data-loss bug that eight of the
  ten copies shared.
- `QUANTUM_STUDY_DATA_DIR` is read on every call instead of once at import,
  so a blank value is no override and `~` is expanded.

## Persistence

All files live in `~/.local/share/quantum-study/` (override the directory
with the `QUANTUM_STUDY_DATA_DIR` environment variable — handy for tests).
The directory is resolved by `common.datadir` **on every call**, so setting
the variable is all a test or a launcher has to do. `persistence.py`
exposes `history_path()`, `flagged_path()`, `settings_path()`,
`mistakes_path()` and `confidence_path()`; the older module constants
(`HISTORY_FILE`, …) are import-time snapshots kept for compatibility.

Every file this app writes now carries a **version sidecar** and a
**rotating backup** — see *Schema versioning and backups* below.

Sessions append to `dojo_history.json`
(schema is integrated against by the coach app — do not change):

```json
[
  {
    "timestamp": 1724800000.0,
    "total": 8,
    "passed": 6,
    "attempts": [
      {"kata_id": "sam_basic", "section": "Sampler", "passed": true, "tries": 2}
    ]
  }
]
```

### Flagged katas

`⚑ Flag for review` maintains `dojo_flagged.json` following the suite-wide
flagging contract (read by `coach.py`'s review queue). Flagging is a
toggle — flagging an already-flagged kata removes its entry:

```json
[
  {
    "id": "dbg_bit_order",
    "label": "Fix it: wrong bit order",
    "category": "Debugging",
    "app": "qiskit-dojo",
    "timestamp": 1724800000.0
  }
]
```

`id` is the kata id, `label` its title, `category` its section. Helpers in
`persistence.py`: `load_flagged()`, `flagged_ids()`, `is_flagged(id)`,
`toggle_flag(kata) -> bool` (new state), `unflag(id)` — all thin wrappers
over `common.flags`, which writes atomically under the file's lock, rebuilds
the file from the raw list (so an unrecognised row is never deleted) and
reads the suite's legacy bare-id form as well as the object form above.

### Mistake journal

A wrong answer should become *analysis*, not just a bookmark. Failing a
kata appends a row to the suite-wide `mistakes.json` — immediately, with
`cause: null`, so nothing is ever lost — and revealing the solution on a
kata you could not pass shows a compact **✎ What went wrong?** row under
the output: one button per cause plus an optional one-line note. It is
skippable, never modal, and never blocks the run loop. Passing the kata
later (this session or a future one) sets `resolved: true`, matched on
`app` + `id`.

```json
[
  {
    "id": "ra_little_endian",
    "app": "qiskit-dojo",
    "category": "Results analysis",
    "question": "Per-qubit probabilities from counts",
    "your_answer": "FAILED: qubit 0 probability was 0.0, expected 0.5",
    "correct_answer": "probs = [...] | assert ...",
    "cause": "knew_but_slipped",
    "note": "little-endian again",
    "timestamp": 1724800000.0,
    "resolved": false
  }
]
```

`cause` is one of `misread`, `didnt_know`, `knew_but_slipped`, `confused`,
`out_of_time`, `other`, or `null` (logged, not yet categorised). `id` is
the kata id and `category` its section. The payload is the *pattern*:
"nine little-endian slips this month" is the signal, which the History
screen surfaces as a per-cause tally of your open mistakes.

Repeated failures on one kata fold into a single open row (the newest
failure headline wins; a cause and note you already chose are kept), so
iterating on a hard kata does not spam the journal.

Helpers in `persistence.py`: `make_mistake_entry(...)` (pure),
`load_mistakes()` / `mistakes_for_app(app)`, `log_mistake(entry)`,
`set_mistake_cause(id, cause, note=None)`, `resolve_mistakes(id)`,
`mistake_cause_counts()`.

### Confidence calibration

Nothing else in the suite distinguishes *right* from *right and knew it*.
The confidence strip pairs the rating you gave before your first Run with
what actually happened, in the suite-wide `confidence.json`:

```json
[
  {
    "id": "ra_little_endian",
    "app": "qiskit-dojo",
    "category": "Results analysis",
    "confidence": 4,
    "correct": false,
    "timestamp": 1724800000.0
  }
]
```

`confidence` is `1` guessing, `2` unsure, `3` fairly sure, `4` certain.
Rated-4-and-wrong rows are the unknown unknowns that sink exam scores;
History shows the per-level tally and the confidently-wrong count.
Only the **first** run of a kata is paired, and a kata you never rated
records nothing.

Helpers: `make_confidence_entry(...)` (pure), `load_confidence()` /
`confidence_for_app(app)`, `log_confidence(id, category, level, correct)`,
`calibration_summary()`, `confidently_wrong(threshold=3)`.

### Analytics file handling

- Both files are **suite-wide**: every app appends to the same
  `mistakes.json` / `confidence.json`, and every mutator here rewrites only
  the rows whose `app` is `qiskit-dojo`, passing foreign rows through
  untouched.
- Both honour `QUANTUM_STUDY_DATA_DIR` like every other data file.
- A missing or corrupt file reads as empty and is recreated on the next
  write — a bad file never crashes the app, and readers never create one.
- Writes are **atomic** (`common.jsonio`): a pid-qualified temp file in the
  same directory, then `os.replace`, so a crash mid-write leaves the
  previous file intact and two processes cannot collide on the temp name.
- Every read-modify-write is held under an `fcntl.flock` on a `<file>.lock`
  sidecar (`common.locking`) and re-reads the file *inside* the lock, so two
  open apps cannot drop each other's rows.
- Growth is **capped**: `MAX_MISTAKES = 2000` and `MAX_CONFIDENCE = 5000`
  (aliases of `common.journal.MISTAKES_MAX` / `CONFIDENCE_MAX`), and only
  **this app's own** oldest rows are ever dropped. The text fields are
  clipped to 200 characters on a single line.

### App settings

`dojo_settings.json` (app-local, new file — no existing schema changed)
holds UI preferences. Today it has one key, written when you press
**Don't ask again** on the confidence strip:

```json
{"confidence_prompt": false}
```

Delete the key (or set it to `true`) to get the strip back. Unknown keys
are preserved on write.

### Schema versioning and backups

The suite now collects data you cannot regenerate. `common.schema` gives
every file this app writes — `dojo_history.json`, `dojo_flagged.json`,
`dojo_settings.json`, and the shared `mistakes.json` / `confidence.json` — a
version marker, a migration path and a safety net.

**The marker is a sidecar, not a key in the data.** `mistakes.json` gains
`mistakes.json.schema.json`:

```json
{"file": "mistakes.json", "kind": "mistakes", "schema": 1,
 "written_by": "common/1.0.0", "updated": 1758600000.0}
```

Wrapping the payload in `{"schema": 1, "rows": [...]}` was not available:
`coach.py` and `dashboard.py` all require the top level to be a plain JSON
list and would read a wrapped file as **empty**. The data files are
therefore byte-for-byte the same shape as before, and `coach.py --review` /
`--mistakes` need no changes. The sidecars are invisible to them, and
`*_flagged.json` discovery does not match `dojo_flagged.json.schema.json`.

- **Older file** — a file with no sidecar is a v1 file (versioning was
  introduced without changing any format). `load_versioned` migrates it
  forward **in memory**; the file on disk is only rewritten, and restamped,
  the next time something writes. Reading is never destructive.
- **Newer file** — a file written by a build that understands a later
  version is **refused, not overwritten**: `save_session` and
  `save_settings` raise `common.schema.SchemaTooNewError` (their callers
  already wrap writes in `try/except`, so the session reports "nothing
  happened" instead of crashing), and the journal helpers swallow it and
  record it in `persistence.last_write_error()`. In every case the file on
  disk is untouched. Reading a newer file still works, so the History
  screen does not go blank when another machine is ahead.
- **Backups** — before the **first** write of a process to a file, the
  current contents are copied aside and the generations age:
  `<name>.bak` → `.bak.1` → `.bak.2`. One backup per session, not per row,
  and best-effort — a full disk must not stop the write that matters.
  `common.schema.restore_backup(path)` puts a generation back.

### Reporting a bad kata

The repository is public, and a wrong kata used to have no route to a fix
except remembering it later. **⚠ Report a problem** on the kata screen
opens `common.ui.errata_dialog.ErrataDialog`: three fields (what is wrong,
what it should say, how bad) over the kata id and the prompt as you saw it.
Accepting builds a URL for the repository's `content_error.yml` issue form
with `file`, `quote`, `why_wrong`, `correction`, `severity` and the title
already filled in, and hands it to `QDesktopServices`.

- **Nothing is sent from the app.** It builds a URL; you see and edit the
  issue on GitHub before filing it. No network call, no API key, no write
  to the data directory.
- **It never blocks.** `openUrl` hands off to the desktop and returns; the
  dialog is an ordinary modal you opened, like Reveal Solution's prompt.
- **It degrades.** When there is no browser to hand the link to, the app
  says so and shows the whole URL, selectable, so the report is not lost.
- **It is keyboard reachable**: a real `StrongFocus` button in the kata
  button row with an accessible name and description, and the dialog's
  "Open the issue on GitHub" stays disabled until you have written
  something.

## Accessibility

The kata screen's new controls follow the suite accessibility rules:

- every button and the note field is a real focusable widget
  (`StrongFocus`) with an accessible name and description, so the whole
  row is reachable and announceable from the keyboard alone;
- the focus ring is an explicit accent border with compensating padding, so
  focus is visible and the button never shifts by a pixel — the rules for
  the default, `#accent`, `#flat` and `#pill` button variants come from the
  shared `common/ui/theme.py` stylesheet, which every app in the suite now
  gets;
- the **⚠ Report a problem** button is a focusable, named control in the
  same row, and its dialog refuses to submit an empty report;
- selection is never colour alone: the confidence buttons carry `○`/`●`
  and the cause buttons a `✓` tick, alongside the existing `✓ PASSED` /
  `✗ FAILED` glyphs on the status line;
- all new text is `TEXT`, `TEXT_MUTED`, `ACCENT` or `WARNING` on `SURFACE`
  / `SURFACE2`, measured at **4.95:1 or better** against the dark palette
  (the weakest pairing is the note field's placeholder, whose colour is
  set explicitly because Qt's default — the text colour at 50% alpha —
  is only 4.36:1).

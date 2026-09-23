# `common/` — the code the ten apps share

Before this package, each of the ten PyQt6 apps carried its own near-identical
copy of the data-directory resolver, the mistake/confidence journal, the
flag-for-review store, the theme palette, four small widgets and an ~900-line
docs Reference screen. Roughly ten thousand duplicated lines, in which every
cross-cutting fix was a ten-way edit — the data-loss race in the journal had to
be fixed ten times — and any one app could silently drift.

This document is the contract. **Migration agents follow it verbatim.**

---

## 1. The import shim — copy this, exactly

The apps are not packages: each is run as `cd <app> && python main.py`, and
several define the same top-level module names (`config`, `core`, `ui`,
`persistence`), so no two can share a `sys.path` and the repository root is not
importable from inside an app.

**Step 1.** Copy `common/app_shim.py` to `<app>/common_path.py`, unedited:

```bash
cp common/app_shim.py <app>/common_path.py
```

**Step 2.** In **every** module of that app that imports from `common`, put
this line above the `common` imports:

```python
import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import journal
from common.ui import theme
```

Every module — not just `main.py`. `persistence.py` is imported directly by
`tests/test_journal_concurrency.py` with no `main` and no `conftest` in the
way, and a screen module is imported directly by that app's UI tests. A module
that assumes something else ran the shim first works right up until the day
something imports it first.

### Why it works in all three cases

| Situation | What happens |
|---|---|
| `cd <app> && python main.py` | `sys.path[0]` is the app dir, so `import common_path` resolves; the shim appends `<repo>`, so `import common` resolves. |
| `cd <app> && python -m pytest` | pytest puts the rootdir (the app dir, which holds its `pytest.ini`) on `sys.path` — the same reason `import persistence` already works there. Same two steps follow. |
| An installed wheel | `common` is an installed package; `import common` works without the shim. The shim finds no checkout, appends nothing, and is a no-op. |

### Why it **appends** rather than `insert(0, …)`

The repository root holds `coach.py`, `dashboard.py`, `launch.py`, `tools/` and
`tests/`. Putting it *before* the app directory would let a root module shadow
an app module of the same name — `import tests` inside an app suite is the
obvious landmine. Appending guarantees the app's own modules always win.

### The shim in full

```python
from __future__ import annotations

import sys
from pathlib import Path


def repo_root() -> Path | None:
    for parent in Path(__file__).resolve().parents:
        pkg = parent / "common"
        if (pkg / "__init__.py").is_file() and (pkg / "journal.py").is_file():
            return parent
    return None


def install() -> Path | None:
    root = repo_root()
    if root is None:
        return None
    text = str(root)
    if text not in sys.path:
        sys.path.append(text)
    return root


ROOT = install()
```

(Two files are checked, not one, so a directory called `common` belonging to
some other project higher up the tree is not mistaken for ours.)

---

## 2. API surface

Nothing outside `common.ui` imports PyQt6, so `coach.py`, `dashboard.py` and
`tools/` can use this package headlessly.

### `common.datadir` — where the data lives

```python
data_dir() -> Path                     # QUANTUM_STUDY_DATA_DIR, else ~/.local/share/quantum-study
ensure_data_dir() -> Path              # the same, created
data_file(name) -> Path                # <data dir>/<name>; rejects a path separator
mistakes_file() -> Path                # <data dir>/mistakes.json
confidence_file() -> Path              # <data dir>/confidence.json
app_file(app, kind) -> Path            # app_file("qec-trainer", "flagged")
default_data_dir() -> Path
ENV_VAR, MISTAKES_FILE, CONFIDENCE_FILE, APP_FILES, APPS
```

**Resolved at call time, never cached.** The ten copies each froze the
directory into a module constant at import time, which is why every app test
had to monkeypatch a different private name. Now
`monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", tmp_path)` is enough, anywhere.

Reconciled: a blank override is no override (`.strip()`, 2 of 10 had it) and
`~` is expanded (3 of 10 had it).

### `common.journal` — `mistakes.json` / `confidence.json`

Pure helpers (no I/O):

```python
clip_text(value, limit=TEXT_MAX) -> str        # one line, ellipsis
clip_note(value, limit=NOTE_MAX) -> str        # keeps line breaks
normalise_cause(cause) -> str | None           # never raises
coerce_confidence(value) -> int | None         # 1..4, else None
make_mistake_entry(item_id, app, category="", question="", your_answer="",
                   correct_answer="", cause=None, note="", timestamp=None,
                   resolved=False) -> dict
make_confidence_entry(item_id, app, category="", confidence=1, correct=False,
                      timestamp=None) -> dict
row_app(row) -> str | None
is_foreign(row, app) -> bool
merge_foreign(disk_rows, entries, app) -> list
trim_own(rows, app, cap) -> list
```

Store (locked, atomic, foreign rows preserved):

```python
load_mistakes(app=None) -> list[dict]
save_mistakes(entries, app) -> bool
log_mistake(entry) -> dict                     # entry from make_mistake_entry
set_mistake_cause(item_id, cause, note=None, *, app) -> dict | None
resolve_mistakes(item_id, app) -> int
open_mistakes(app=None) -> list[dict]
mistakes_for(item_id, app=None) -> list[dict]
cause_counts(app=None, *, include_resolved=True, include_uncategorised=True,
             entries=None) -> dict[str, int]

load_confidence(app=None) -> list[dict]
save_confidence(entries, app) -> bool
log_confidence(item_id, app, category="", confidence=None, correct=False,
               timestamp=None) -> dict | None
calibration_summary(app=None, entries=None) -> dict[int, dict[str, int]]
confidently_wrong(app=None, *, min_confidence=3, entries=None) -> list[dict]
confidently_wrong_by_category(app=None, *, min_confidence=3) -> dict[str, int]

last_write_error() -> SchemaError | None       # a refused write, if any
clear_write_error() -> None
mistakes_path() / confidence_path() -> Path
lock                                           # re-exported from common.locking
```

Constants: `MISTAKE_CAUSES`, `CAUSE_LABELS`, `UNCATEGORISED`,
`CONFIDENCE_LEVELS`, `CONFIDENCE_LABELS`, `CONFIDENT_LEVEL`, `TEXT_MAX`,
`NOTE_MAX`, `MISTAKES_MAX`, `CONFIDENCE_MAX`, `MISTAKE_KEYS`,
`CONFIDENCE_KEYS`.

`app` is the **app directory name** (`"qec-trainer"`) — what `coach.py` and
`dashboard.py` group by. It is required, not defaulted, in every function that
writes: a row with the wrong owner is written back by the wrong app's merge and
is effectively lost. In `set_mistake_cause` it is keyword-only for the same
reason.

### `common.flags` — `<prefix>_flagged.json`

```python
make_label(text, limit=80) -> str
make_id(*parts, prefix="") -> str              # sha256 for generated items
flagged_path(app) -> Path
load_raw(path) -> list                         # the file as stored
load_flagged(path, app) -> list[dict]          # normalised, legacy shapes too
flagged_ids(path, app="") -> set[str]
is_flagged(path, flag_id, app="") -> bool
save_flagged(path, rows, app) -> bool
toggle_flag(path, flag_id, label="", category="", *, app) -> bool
flag(path, flag_id, label="", category="", *, app) -> bool
unflag(path, flag_id, *, app) -> bool
```

Reads both the contract shape (`[{id, label, category, app, timestamp}]`, seven
apps) and the legacy bare-id list (`["id", "id"]` — `flagged_cards.json`,
`qec_flagged.json`, `vqa_flagged.json`); writes the contract shape, so a legacy
file upgrades itself on its first write. `coach.py` parses both, so nothing
breaks either way.

### `common.schema` — versions, migration, backups

```python
FileSchema(kind, version=1, baseline=1, migrations={}, description="")
register(schema, *, replace=False) / unregister(kind) / get(kind) / kinds()
sidecar_path(path) -> Path                     # mistakes.json.schema.json
read_meta(path) -> dict
stored_version(path, kind) -> int
write_meta(path, kind, *, version=None)
migrate_payload(payload, kind, from_version) -> (payload, steps)
load_versioned(path, kind, reader=None)        # migrates forward in memory
save_versioned(path, payload, kind, *, backup=True, indent=2)
check_writable(path, kind)                     # raises SchemaTooNewError
backup_paths(path, keep=3) / rotate_backup / backup_once / reset_session
restore_backup(path, generation=0, keep=3) -> bool
SchemaError, SchemaTooNewError, UnknownKindError
```

Registered kinds: `mistakes`, `confidence`, `flagged`, `history`, `settings`,
`schedule` — all at v1 with no migrations, because the sidecar was introduced
**without changing any on-disk format**.

**The marker is a sidecar file, not a key in the data**, because every existing
reader requires the top level to be a plain JSON list:

- `dashboard._read_journal`, `dashboard._load`, `coach._load_list` all do
  `return data if isinstance(data, list) else []`.

A `{"schema": 1, "rows": [...]}` wrapper would make all three read the file as
**empty** — the whole mistake journal would vanish from `coach --mistakes` and
the dashboard. A sentinel row inside the list would survive those three but be
dropped by `dashboard.normalise_mistake` and would have to be skipped by hand in
nine other places, one of which would be missed. The sidecar is invisible: those
readers open one exact file name, and `mistakes.json.schema.json` is not it.
`tests/test_common_schema.py` runs the real `coach.py` / `dashboard.py` loaders
against a directory with sidecars in it and asserts they still see every row.

Backups: before the **first** write of a process to a file, the current contents
are copied to `<name>.bak`, ageing `<name>.bak` → `<name>.bak.1` →
`<name>.bak.2`. Three generations, one backup per session, best-effort.

### `common.errata` — prefilled GitHub issues (pure, offline)

```python
issue_url(app, item_id="", item_text="", comment="", *, severity="wrong",
          correction="", repo=REPO, template="content_error.yml",
          max_url=6000) -> str
issue_body(app, item_id="", item_text="", comment="", *, severity="wrong",
           correction="") -> str
issue_title(app, item_id="", *, prefix="[content] ") -> str
item_location(app, item_id="") -> str
issue_base_url(repo=REPO) -> str
REPO, TEMPLATE, LABELS, SEVERITIES, DEFAULT_SEVERITY, APP_ITEM_PATHS, MAX_URL
```

Targets `.github/ISSUE_TEMPLATE/content_error.yml` and mirrors its field ids
(`file`, `quote`, `why_wrong`, `correction`, `severity`), so the report lands in
the right boxes. `template=None` falls back to a plain prefilled body.

### `common.jsonio` / `common.locking`

```python
read_json(path, default=None) / read_json_list / read_json_dicts / read_json_dict
atomic_write_json(path, payload, *, indent=2, ensure_dir=True)

lock(path, timeout=5.0, create=False)          # context manager, yields bool
lock_path_for(path) -> Path                    # <path>.lock
```

`lock` is the extracted `journal_sync.lock`: bounded, always released,
re-entrant, and it *degrades* (yields False) rather than raising on a
filesystem that cannot lock.

### `common.ui.theme`

The twelve palette constants (`BG`, `SURFACE`, `SURFACE2`, `BORDER`, `ACCENT`,
`ACCENT2`, `TEXT`, `TEXT_MUTED`, `SUCCESS`, `WARNING`, `ERROR`, `PARTIAL`) were
**byte-identical in all ten apps**, so this is not a compromise. Also `FLAG`
(exam-sim's name for `PARTIAL`), `PURPLE`/`TEAL`, `FOCUS`/`FOCUS_ON_ACCENT`,
`CODE_FG`, `MONO`/`MONO_FAMILY`/`MONO_FAMILIES`, `UI_FONT`/`UI_FAMILIES`,
`COLLAPSIBLE_ANIMATION_MS`, `SCORE_BAR_ANIMATION_MS`, plus:

```python
alpha(color, percent) -> str                   # "#58a6ff" + 13% -> "#58a6ff21"
QSS                                            # the base stylesheet
extend(extra="") -> str                        # base + the app's own rules
apply(app, stylesheet=None) -> None
```

Keep the app's **own vocabulary** (`CATEGORY_COLORS`, `DIFFICULTY_COLORS`,
`SECTION_COLORS`, `TOPIC_COLORS`, `QTYPE_COLORS`, `subject_color()`) in the
app's `ui/theme.py`, which becomes a dozen lines:

```python
import common_path  # noqa: F401
from common.ui.theme import *          # noqa: F403
from common.ui.theme import apply as _apply, extend

CATEGORY_COLORS = {...}                # this app's vocabulary
_EXTRA = "QLabel#myThing { ... }"

def apply(app):
    _apply(app, extend(_EXTRA))
```

### `common.ui.widgets`

```python
LoadingOverlay(parent, message="Working…")
    .show_message(main, sub="")        # .show_with_message is an alias
    .hide_overlay()
CollapsiblePanel(title, content_widget, parent=None, *, duration_ms, expanded=False)
    .expanded / .set_expanded(bool)
PillBadge(text, color, parent=None).update_text(text, color)
ScoreBar(parent=None, *, blocks=10, duration_ms).animate_to(v) / .set_score(v)
block_color(index, blocks=10) -> QColor
```

### `common.ui.reference`

```python
ReferenceScreen(parent=None, *, default_chapter="", category_docs=None,
                docs_root=None, title="Reference")
    signals: back_requested, doc_opened(str)
    .load_all() / .reload()
    .open_doc(rel_path, fragment=None) -> bool
    .show_chapter(chapter_dir) / .show_category(category) -> bool
    .set_search(text) / .visible_titles() / .docs_root()
    .entries / .current_entry / .current_doc_path() / .category_docs

docs_root() -> Path                    # QUANTUM_STUDY_DOCS_DIR, else found
scan_docs(root=None) -> list[DocEntry]
corpus_signature(root=None) -> tuple
iter_docs(root) / read_title(path) / pretty_words / pretty_chapter / list_label
prepare_markdown(text, doc_dir=None, show_solutions=True, root=None) -> str
resolve_doc_ref(ref, doc_dir, root=None) -> str | None
heading_slug(text) -> str
restyle_document(doc) -> None
DOCS_ENV_VAR, ALL_CHAPTERS, OVERVIEW_CHAPTER, JUMP_PLACEHOLDER, DocEntry
```

The two per-app differences are the two constructor arguments:

```python
self.reference = ReferenceScreen(
    default_chapter="05_quantum_error_correction",
    category_docs={
        "Surface Code": "05_quantum_error_correction/06_surface_code.md",
    },
)
```

An app with no `category_docs` simply gets no "Jump to topic" picker — the
control hides itself. The docs root is resolved **at call time** from the
package location, then the cwd, then `sys.argv[0]`, so it works from any app
directory; `QUANTUM_STUDY_DOCS_DIR` overrides it.

### `common.ui.errata_dialog`

```python
ErrataDialog(parent=None, *, app, item_id="", item_text="", repo=REPO)
    .exec() -> int ; .issue_url -> str | None ; .build_url() -> str
ErrataButton(parent=None, *, app, item_id="", item_text="", repo=REPO,
             open_browser=True, text="⚑ Report an error")
    .set_item(item_id, item_text="") ; .report() -> str | None
    signal: reported(str)
```

---

## 3. Divergences reconciled, and what was chosen

Recorded here because "which copy was right?" is the question a migration keeps
asking.

| Divergence | Chosen | Why |
|---|---|---|
| Journal growth cap trimmed the newest *N* rows of the **whole file** (8 apps) vs only the app's own rows (paper-drill) | **Own rows only** (`trim_own`) | The other eight sorted the merged list by timestamp and kept the newest *N* — silently deleting **other apps' rows** during a write to a file they do not own. A data-loss bug. |
| `log_mistake` merged a repeat into the open row (qec-trainer) vs appended (8 apps) | **Append** | `dashboard.load_mistakes` says it outright: "a genuine second miss of the same item keeps its own entry, because repetition is exactly the signal". Merging destroys the count `coach --mistakes` reports. |
| `set_mistake_cause(note="")` always overwrote the note (paper-drill) vs left it alone when None (qec, vqa) | **`note=None` keeps it, `note=""` clears it** | paper-drill's signature wiped a note whenever a cause was picked after the note had been typed. |
| Unknown cause raised `ValueError` (math-quiz, exam-sim) vs stored `None` (6 apps) vs lower-cased first (vqa) | **Never raise; strip + lower-case, then `None` if unknown** | A stray cause value must not cost the mistake itself. vqa's normalisation makes `"Misread"` match. |
| `calibration_summary` buckets `{"n", "correct"}` (qec) vs `{"total", "correct"}` (qiskit-dojo, math-quiz) | **`{"total", "correct"}`** | `n` is not self-describing next to `correct`. |
| `log_confidence` clamped a bad rating into 1..4 (vqa) vs rejected it (qec, paper-drill) | **Reject** (the pure builder still clamps) | Clamping invents a rating the learner never gave and then reports on it. `None` means "the strip was skipped". |
| Text clipping truncated hard (qec, vqa) vs collapsed whitespace and added `…` (paper-drill, quantum-quiz) | **Collapse + `…` for one-line fields; the note keeps its line breaks** | A question with a newline breaks a one-line list row; a note is prose the user typed and reflowing it destroys deliberate structure. |
| `CAUSE_LABELS["didnt_know"]` — ASCII `"Didn't know"` (7 apps), typographic `"Didn’t know"` (vqa), `"Knew it, slipped"` &c. (exam-sim) | **The ASCII seven** | exam-sim's rewordings were a local edit, not a considered change. |
| Data dir: `.strip()` on the override (2 of 10), `.expanduser()` (3 of 10) | **Both** | Without `strip`, `QUANTUM_STUDY_DATA_DIR=" "` gave eight apps a directory literally named `" "`. Without `expanduser`, an unexpanded `~/scratch` made a directory called `~` in the cwd. |
| Flag file rewritten from the *filtered* list (5 apps) vs the raw list (quantum-quiz) | **Raw list** | Rewriting from the filtered list deletes rows the app did not understand. |
| Flag file written with `write_text` (4 apps) vs atomically (6 apps) | **Atomic** | `write_text` truncates first: a crash mid-write lost every flag. |
| `LoadingOverlay` plain (5 apps) vs animated with a sub-label (3 apps) | **Animated** | A strict superset, and a static "Grading…" over a frozen window is indistinguishable from a hang. The plain family also resized against `self.parent()` (the *QObject* parent, which may have no `size()`); `parentWidget()` is correct. Five copies had no `hide_overlay()` and left the timer running. |
| Focus-visible stylesheet rules (qec, vqa only) and `QPushButton#pill` rules (5 apps) | **In the base stylesheet for everyone** | Keyboard focus visibility is an accessibility requirement, and every app now has confidence/cause pills. |
| `_atomic_write_json` temp name: fixed `.tmp` (several) vs pid-qualified (several) | **pid + counter** | With a fixed name, two processes writing at once truncate each other's temp file and one `os.replace`s a partial file into place. |

---

## 4. What deliberately did **not** move

- **Per-app colour vocabulary** (`CATEGORY_COLORS`, `SECTION_COLORS`, …) — not
  shared style, just this app's words.
- **Per-app file names and history schemas.** `<prefix>_history.json` is parsed
  by `coach.py` and `dashboard.py`; those schemas are load-bearing and are
  untouched. `common.datadir.APP_FILES` records the names, nothing more.
- **`ui/main_window.py`, the setup/summary/history screens, the graders.** They
  look similar and are not: each encodes its own app's session model.
- **`journal_sync.py`.** The ten byte-identical copies stay until their apps
  migrate; `common.locking` is the extraction, and
  `tests/test_journal_concurrency.py` still asserts the ten copies match each
  other. Delete an app's copy in the same commit that switches it to
  `common.journal`.

---

## 5. Tests

`tests/test_common_*.py` live in the **root** suite (`tests/`), which imports no
app and is therefore safe to run in one process:

| File | Covers |
|---|---|
| `test_common_shim.py` | the shim from a simulated app dir, running a script and running pytest |
| `test_common_datadir.py` | override, blank override, `~`, call-time resolution, `app_file` |
| `test_common_journal.py` | pure helpers, foreign-row preservation, caps, multi-process concurrency (and the same test failing against a deliberately unlocked variant) |
| `test_common_flags.py` | toggle, legacy bare-id upgrade, unknown-row preservation, atomicity |
| `test_common_schema.py` | migration up, refusal to write a newer file, backup rotation, and `coach.py` / `dashboard.py` still reading a directory with sidecars |
| `test_common_errata.py` | URL shape, field ids, escaping, truncation |
| `test_common_reference.py` | docs discovery, titles, labels, `$$`/`<details>` rewriting, slugs, cross-reference resolution |

Run them with `bash tools/run_tests.sh` (all eleven suites) or
`.venv/bin/python -m pytest tests/ -k common` for these alone.

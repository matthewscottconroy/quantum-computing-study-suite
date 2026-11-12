# `quantum_study.common` — the code the ten apps share

One implementation of everything that is the same in every app: where the study
data lives, the mistake and confidence journals and the lock that guards them,
the flag-for-review store, schema versions and backups, errata links, the
shuffled display order for multiple-choice options, the Claude model id, and
the Qt pieces under `ui/` — theme, widgets and the docs Reference screen.

```python
from quantum_study.common import datadir, journal
from quantum_study.common.ui import theme
```

Nothing outside `common.ui` imports PyQt6, so `coach.py`, `dashboard.py` and
`tools/` use the package headlessly. Each app keeps its own `config.py`,
`persistence.py` and `ui/theme.py` as thin adapters over what is here, so an
app's vocabulary (its categories, its colours, its history file) stays its own.

Two small modules have no section below because they are one name each:
`llm.MODEL` is the Claude model id for every app, and `testing` holds what the
repository's root `conftest.py` turns into fixtures (`isolate_data_dir`,
`qapplication`, `settle_qt`).

---

## API surface

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

### `common.choices` — display order for multiple-choice options

```python
display_order(n_options, rng=None) -> list[int]   # order[row] = bank index shown in that row
resolve_order(order, n_options) -> list[int]      # order if a valid permutation, else bank order
row_of(order, bank_index) -> int | None           # the row a bank index is shown in
positional_reference(option) -> str | None        # "Both A and C", "all of the above", …
```

The banks key most answers at index 0, so a screen that shows options in
stored order makes "always pick A" a passing strategy. Shuffle at **display**
time only: the bank, the history files, the journal and the graders keep
speaking in bank indices, and the screen translates through `order`. Nothing
on disk changes shape. Used by exam-sim (exam and review screens),
qec-trainer and vqa-trainer (problem screens); `coach.py --diagnostic` does
the same thing inline. Each bank's tests call `positional_reference` so an
option can never depend on where it is shown.

### `common.jsonio` / `common.locking`

```python
read_json(path, default=None) / read_json_list / read_json_dicts / read_json_dict
atomic_write_json(path, payload, *, indent=2, ensure_dir=True)

lock(path, timeout=5.0, create=False)          # context manager, yields bool
lock_path_for(path) -> Path                    # <path>.lock
```

`lock` is bounded, always released,
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
from quantum_study.common.ui.theme import *          # noqa: F403
from quantum_study.common.ui.theme import apply as _apply, extend

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

## Tests

`tests/test_common_*.py`, in the root suite:

| File | Covers |
|---|---|
| `test_common_datadir.py` | override, blank override, `~`, call-time resolution, `app_file` |
| `test_common_journal.py` | pure helpers, foreign-row preservation, caps, multi-process concurrency (and the same test failing against a deliberately unlocked variant) |
| `test_common_flags.py` | toggle, legacy bare-id upgrade, unknown-row preservation, atomicity |
| `test_common_schema.py` | migration up, refusal to write a newer file, backup rotation, and `coach.py` / `dashboard.py` still reading a directory with sidecars |
| `test_common_errata.py` | URL shape, field ids, escaping, truncation |
| `test_common_choices.py` | permutation, uniformity, seeded reproducibility, fallback to bank order, position-dependent option detection |
| `test_common_reference.py` | docs discovery, titles, labels, `$$`/`<details>` rewriting, slugs, cross-reference resolution |
| `test_common_ui.py` | theme, widgets and the errata dialog, offscreen |
| `test_journal_concurrency.py` | ten apps (and three windows of one app) appending at once lose no rows |
| `test_qt_fixture.py` | one `QApplication` for the whole run; `settle_qt` really destroys what a test left behind |

Run them with `pytest tests -k "common or journal or qt_fixture"`.

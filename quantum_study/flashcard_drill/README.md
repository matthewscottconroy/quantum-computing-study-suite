# Flashcard Drill

A spaced-repetition flashcard app for quantum computing — the only app in the suite that
requires no API key and no Qiskit. 550 cards across 14 categories, with a real **SM-2
scheduler** (due dates and a daily pull — "23 cards due today"), SRS-weighted free drills,
an optional per-card countdown timer, flag-for-review, a **mistake journal** and
**confidence calibration**, an in-app Reference browser for the shared docs corpus, and full
session history.

Its journal, flag store, data-directory resolution, theme and Reference screen come from
the suite's shared [`common/`](../common/README.md) package, so a fix made once reaches
all ten apps; every file it writes is version-stamped, migrated forward and backed up by
`common.schema`; and a wrong card can be reported from inside the drill as a prefilled
GitHub issue.

---

## Features

- **550 cards across 14 categories** — Pauli matrices, gate unitaries, commutators,
  complexity, theorems, quantum information, algorithms, quantum circuits, error
  correction, states and measurement, quantum hardware, quantum optics,
  many-body physics, and the Qiskit API (exam C1000-179 aligned)
- **SM-2 spaced repetition** — every rating gives the card an ease factor, an interval and
  a due date; the setup screen opens with "N cards due today" and a *Due today* session
  mode that draws exactly that queue (oldest due first, topped up with new cards)
- **Free drill** — the original weighted mix: cards you missed recently appear more often
- **Optional countdown timer** — configurable per session; timer turns red at 5 s
- **Three-way rating** — Got it / Unsure / Missed after each reveal
- **Flag for review** — mark any card after revealing it; drill only flagged cards, and
  review / unflag them from the History screen
- **Mistake journal** — a *Missed* rating is logged to the suite-wide `mistakes.json`
  together with *why* you missed it (misread / didn't know / knew but slipped / confused /
  out of time / other). A wrong answer stops being a bookmark and becomes analysis: "nine
  little-endian slips this month" is the signal, not nine flagged cards. Skippable, never
  modal, and rating the card *Got it* later resolves the entry
- **Confidence calibration** — an optional 1–4 strip on the card **front**, before the
  answer can be seen, paired with the grade in `confidence.json`. It finds the
  *confidently wrong* topics — the unknown unknowns nothing else in the suite surfaces
- **Reference browser** — read every chapter of the suite's `docs/` corpus inside the
  app, with chapter filter, full-text search and hideable exercise solutions
- **Report a problem with this item** — the revealed answer carries a
  *⚠ Report a problem with this item* button that opens a prefilled GitHub issue for that
  card (its id, both sides of it, what you say is wrong, an optional correction and a
  severity). The repository is public; this is the path from "this card is wrong" to a
  fix. It never blocks the drill and, on a machine with no browser, puts the URL on the
  clipboard and says so
- **Browse mode** — read-only view of every card by category
- **Session history** — lifetime totals plus a % Known trend chart
- **Versioned, backed-up data** — every file the app writes carries a
  `<file>.schema.json` version marker, is migrated forward when its format changes, is
  refused (never overwritten) if a newer build wrote it, and keeps three generations of
  backup of the state each session started from
- **Minimal dependencies** — only PyQt6 and matplotlib (history chart) required

---

## Requirements

```
PyQt6>=6.6
matplotlib>=3.8
```

Install:
```bash
pip install PyQt6 matplotlib
```

---

## Running

```bash
python main.py
```

No API key, no network connection needed. Keep the `flashcard-drill/` folder inside the
`Quantum-Computing` checkout: the Reference screen resolves `docs/` relative to its own
source file (never from a hard-coded path), so the working directory does not matter.

---

## Usage

### Setup Screen

At the top sits **today's pull**: `23 cards due today`, with the breakdown underneath
(`4 overdue · 120 scheduled · 430 new · 550 in scope`) and a **Review Due Cards** button
that starts the queue in one click. With nothing due it reads `Nothing due today` plus
the next review date; before your first rating it reads `No review schedule yet`.

1. **Session mode**
   - *Due today — spaced repetition*: draws the cards SM-2 says are due (oldest due
     first), then fills the rest of the session with cards you have never seen
   - *Free drill — weighted mix*: the original sampler (unchanged) — recently missed
     cards come up more often. Ratings still update the SM-2 schedule.

   The mode is preselected for you — *Due today* when something is due, *Free drill*
   otherwise, including on a fresh install — and once you pick one by hand it is left
   alone.
2. **Select categories** — all 14 checked by default; each row shows a mastery bar
   derived from your history. The due counts follow the selection.
3. **Card count** — how many cards to draw this session (default 20)
4. **Time limit per card** — No timer / 10 / 20 / 30 / 60 s
5. **Show Flagged Only** — drill just the cards you have flagged (ignores categories and
   the schedule); *Start Drill* stays disabled until at least one card is flagged
6. **Self-assessment** — *Ask my confidence before each reveal* switches the confidence
   strip on the card screen on or off. It is the same setting the card screen's
   *Don't ask* button writes, so the tick box always shows the current state
7. Click **Start Drill**

In *Due today* mode with nothing due and no new cards left, *Start Drill* is disabled and
its tooltip says when to come back.

Once you have rated a few cards, an "≈ N min" estimate under the card count uses your
median seconds-per-card from past sessions.

Footer buttons: **View History**, **Browse Cards**, **Reference**.

### Card Screen

- The **front** of the card is shown centred in the card frame
- **How sure are you?** — an optional 1–4 strip under the front: `1 Guessing`,
  `2 Unsure`, `3 Fairly sure`, `4 Certain` (keys `1`–`4`, *before* the reveal). It
  disappears the moment the answer is shown, so the rating can never be hindsight.
  Click the same button again to clear it, or **Don't ask** to switch the strip off for
  good (the Setup screen's *Self-assessment* tick box turns it back on)
- Click **Reveal Answer** (or press Space / Enter, or wait for the timer) to flip the card
- Rate yourself (buttons or keys `1` / `2` / `3`). The card screen keeps keyboard focus
  itself (no button in the drill flow can take focus), so the shortcuts work after mouse
  clicks too
  - **Got it** — you knew the answer confidently
  - **Unsure** — you had partial recall
  - **Missed** — you did not know the answer
- **✗ Missed · … / Answer: …** — rating a card *Missed* journals it straight away and
  raises a compact **What went wrong?** row carrying the question and the answer. Pick a
  cause (*Misread*, *Didn't know*, *Knew but slipped*, *Confused*, *Out of time*, *Other*),
  add an optional one-line note, or ignore it entirely — the mistake is already logged with
  `cause: null`, so nothing is lost. The drill **never waits**: the next card is already on
  screen and there is no dialog to close. `W` jumps into the row, Escape or **✕ Dismiss**
  closes it, and rating the next card closes it too
- **⚑ Flag for Review** appears after the reveal; it is a toggle — click again to unflag
- **⚠ Report a problem with this item** sits beside it. It opens a small form (what is
  wrong / what it should say / how bad) and then a **prefilled GitHub issue** in your
  browser, carrying the card id, the card's file path and both sides of the card exactly
  as you just read them. Nothing is sent until you submit it on GitHub. The dialog is
  *opened*, not run in a nested event loop, so the countdown keeps ticking and the drill
  is never frozen; if no browser can be opened the URL goes to your clipboard and the
  button's own label says so until the next card
- **End Session** finishes early (rated cards are still saved; with nothing rated it
  simply returns to Setup and nothing is written)

Repeat until all cards are done; the session summary appears automatically.

Both review features are additive. Your ratings, history, flags and SM-2 schedule behave
exactly as they did before: **a journalled mistake is analysis, not a second lapse**, so it
never touches `flashcard_schedule.json`.

#### Accessibility

Every control added by these three features is Tab-reachable with a 2 px accent focus ring
and an accessible name, and hands focus straight back to the card screen when activated so
Space / `1`–`3` keep working (the errata button included: Tab reaches it, Space opens
its dialog, and closing the dialog hands focus back to the card). Selected state is never
colour alone — the buttons carry a
`○` / `●` glyph — and the missed-card header pairs its red with the `✗` glyph and the word
"Missed". Every new label clears 4.5:1 against the dark palette (body text `#e6edf3` on
`#21262d` is 12.9:1, muted `#8b949e` on `#161b22` is 6.1:1, the `✗ Missed` header `#f85149`
on `#0d1117` is 5.7:1, and a selected button is `#0d1117` on `#58a6ff` at 7.5:1).

### Summary Screen

- % Known headline plus Got it / Unsure / Missed counts
- **Schedule line** — how the session moved the deck:
  `8 graduated to a longer interval · 2 lapsed back to 1 day · longest interval now
  15 days · next review tomorrow (14 cards)`
- Per-category mini-cards and a detail table
- **Review Missed** re-drills only the cards you missed (shown when there were any)
- **Drill Again** with the same configuration, or **Back to Setup**

### History Screen

- Lifetime stat cards: sessions, cards seen, % known
- **% Known trend** line chart over the last 30 sessions (70 % target line)
- **Flagged for review** — every flagged card with its category and prompt, each with an
  **Unflag** button; IDs whose card file no longer exists are listed so they can be
  cleaned up too
- **← Back to Setup**

### Reference Screen

The suite-wide Reference screen (`common.ui.reference.ReferenceScreen`) — an in-app
browser for the shared study docs (`<repo>/docs/**/*.md`). This app has no chapter of its
own in the corpus and no topic map, so it takes the defaults: the whole corpus, opened on
its README, and no "Jump to topic" picker.

- **Chapter filter** (Start Here / Ch 1 … Ch 8) and a navigation list grouped by chapter;
  the landing page is `docs/README.md`, the learning ladder
- **Search** matches titles and full text; the list shows hit counts per doc and the
  reader jumps to the first occurrence
- **Show solutions** — exercise `<details>` blocks are rendered as "▸ Solution"
  sections; untick to hide them and quiz yourself first
- Cross-references between docs open in place — both Markdown links and the bare
  `NN_chapter/NN_file.md` / `NN_file.md` references the corpus writes in prose (with an
  optional `#heading` suffix) — `#anchors` scroll to the heading, and external URLs open
  in your browser
- **← Back** returns to Setup

Rendering uses Qt's built-in Markdown engine (no extra dependency) restyled for the dark
theme; `$$ … $$` display math in a doc is shown as a monospaced block (kept inside its
block quote when the formula is part of one).

The corpus is found at call time (from the package, then the working directory, then
`sys.argv[0]`), and `QUANTUM_STUDY_DOCS_DIR` overrides it — this app no longer hard-codes
`parents[3] / "docs"`.

---

## Card Categories and Counts

| Category | Cards | Sample Topics |
|---|---|---|
| Pauli Matrices | 48 | X, Y, Z matrices; eigenvalues; commutation/anticommutation; Bloch sphere axes |
| Gate Unitaries | 52 | H, S, T, CNOT, CZ, SWAP, Toffoli matrices; eigenvalues; decompositions |
| Quantum Info | 47 | Von Neumann entropy, fidelity, trace distance, Holevo bound, channel capacity |
| Qiskit API | 45 | QuantumCircuit construction, primitives (SamplerV2/EstimatorV2), transpilation, quantum_info, visualization, OpenQASM |
| Algorithms | 44 | Grover speedup, QPE circuit, QFT structure, Shor period-finding, HHL conditions |
| States & Measurement | 44 | Bell states, Bloch sphere, Born rule, measurement bases, entanglement |
| Commutators | 43 | [X,Y], [H,X], [X,Z]; uncertainty principle; commuting observables; Pauli algebra |
| Complexity | 42 | BQP, QMA, PSPACE; oracle separations; Grover optimality; Shor complexity |
| Theorems | 42 | No-cloning, Solovay-Kitaev, Gottesman-Knill, threshold theorem, Eastin-Knill |
| Quantum Circuits | 40 | Ancillas, Clifford simulation, circuit identities, amplitude amplification |
| Error Correction | 39 | 3-qubit codes, stabilizers, CSS codes, surface and color codes, cat qubits |
| Quantum Hardware | 22 | Josephson junctions, gate fidelity, crosstalk, connectivity, dilution refrigerators |
| Quantum Optics | 21 | Beam splitters, Fock and coherent states, cavity QED, GKP states, boson sampling |
| Many-Body Physics | 21 | Hubbard and Heisenberg models, area law, DMRG, QITE, Jordan-Wigner/Bravyi-Kitaev |

**Total: 550 cards**

---

## Spaced Repetition

Two independent mechanisms, both fed by the same three ratings:

| | Scheduler (SM-2) | Free-drill weighting |
|---|---|---|
| Question it answers | *when* should this card come back? | *which* cards should this session sample? |
| State | `flashcard_schedule.json` (per card: `n`, `EF`, interval, due date) | derived on the fly from `flashcard_history.json` |
| Used by | *Due today* mode, the due counts on the setup screen | *Free drill* mode |

Every rating updates the schedule, whichever mode you drilled in.

---

## SM-2 Scheduler (`core/scheduler.py`)

Pure functions over an immutable `CardState` (`card_id`, `n`, `ef`, `interval_days`,
`due`, `last_seen`, `lapses`) — no Qt, no file I/O, so the maths is unit-testable on its
own. The app's three ratings map onto three SM-2 grades:

| Rating | Grade | Effect |
|---|---|---|
| **Missed** | `again` | lapse: `n → 0`, `I → 1` day, `EF −= 0.20`, `lapses += 1` |
| **Unsure** | `hard` | `n += 1`, `EF −= 0.15`, `I → max(1, round(I × 1.2))` |
| **Got it** | `good` | `n += 1`; `I → 1` (n=1), `6` (n=2), else `round(I × EF)`; then `EF += 0.10` |

```
EF  clamped to [1.3, 2.5]        (2.5 is both the start and the ceiling)
I   clamped to [1, 365] days
due = review date + I
```

The interval for a *good* review uses the ease factor **before** the `+0.10` bonus, and
ties round toward zero (`37.5 → 37`), so a card answered "Got it" five times walks the
classic SM-2 ladder:

```
rep   1     2     3      4      5
I     1d    6d    15d    37d    92d        (6×2.5, 15×2.5, 37×2.5)
```

Because the ceiling equals the starting ease, the `+0.10` bonus only ever *repays* ease
lost to Unsure/Missed — a perfect card never inflates past the textbook ladder, while a
card that lapsed three times (`EF = 1.9`) climbs `1, 6, 13, …` instead. `EF` can never
fall below `1.3`, so no card becomes unschedulable. A miss on a card you had never
learned resets the interval and the ease but is not counted as a lapse.

### The daily pull

`select_due_ids(states, candidate_ids, limit)` returns the session queue: every card whose
`due` date is today or earlier, **oldest due first**, then never-seen cards in the caller's
order until `limit` is reached. Cards scheduled for a later day are never drawn.
`summarise(...)` produces the counts behind the banner (due / overdue / scheduled / new /
next review date).

Simulated over 90 days with 200 cards and a fixed seed (see
`tests/test_schedule_simulation.py`), the backlog stays bounded — it never exceeds twice a
day's workload — and every card is introduced instead of starving behind reviews.

---

## Free-Drill Weighting

Session history is read from `flashcard_history.json` (see Data Persistence) every time
a free-drill deck is built. Each past session is weighted by an exponential decay with a 14-day half-life,
and the weight for each card is computed as:

```
ease_map = { got_it: 1.0, unsure: 0.5, missed: 0.0 }
w(session) = 2^(-age_days / 14)

For each session:
    weighted_ease[card_id]  += w(session) × ease_map[rating]
    weighted_count[card_id] += w(session)

ease_score[card_id] = weighted_ease[card_id] / weighted_count[card_id]
weight[card_id]     = max(0.1, 1.0 - ease_score[card_id])
```

Cards you got right recently have ease ≈ 1.0 → weight ≈ 0.1 (rarely sampled).
Cards you missed recently have ease ≈ 0.0 → weight ≈ 1.0 (frequently sampled).
Cards with no history get weight 1.25 (slightly favoured over missed cards so new
material keeps entering rotation). The minimum weight is 0.1 so no card is permanently
excluded.

### Deck Building

`build_deck(config)` in `core/deck.py`:
1. *Due today* (`config.due_only`) hands off to `build_due_deck()` → the SM-2 queue above
2. Otherwise pool = flagged cards (if *Show Flagged Only*) or all cards in the chosen
   categories
3. Draw `k` cards with replacement using `random.choices(pool, weights=weights, k=k)`
4. Deduplicate while preserving the weighted order
5. If fewer unique cards were drawn than requested, fill from a uniform shuffle of the
   remaining unselected cards

---

## Architecture

```
flashcard-drill/
├── main.py
├── common_path.py               the import shim: a verbatim copy of common/app_shim.py
│                                that puts the repository root on sys.path
├── config.py                    APP name, window defaults, and the path of every file
│                                this app writes (resolved at call time)
├── core/
│   ├── models.py                Flashcard, DrillConfig, Rating, CardResult, SessionStats
│   ├── scheduler.py             SM-2: CardState, review(), select_due_ids(), summarise()
│   └── deck.py                  build_deck(config) — due-today queue or weighted sampling
├── cards/
│   ├── __init__.py              all_cards(): auto-discovers one card file per card
│   ├── pauli_matrices/          48 cards
│   ├── gate_unitaries/          52 cards
│   ├── quantum_info/            47 cards
│   ├── qiskit_api/              45 cards
│   ├── algorithms/              44 cards
│   ├── states_and_measurement/  44 cards
│   ├── commutators/             43 cards
│   ├── complexity/              42 cards
│   ├── theorems/                42 cards
│   ├── quantum_circuits/        40 cards
│   ├── error_correction/        39 cards
│   ├── quantum_hardware/        22 cards
│   ├── quantum_optics/          21 cards
│   └── many_body_physics/       21 cards
├── journal_sync.py              **unused by the app** — the pre-migration lock module,
│                                kept only because tests/test_journal_concurrency.py
│                                asserts the ten app copies are byte-identical (see
│                                "Known issues" below).  common.locking is the live one
├── persistence/
│   ├── storage.py               flashcard_history.json + flagged_cards.json:
│   │                            save_session(), card_weights(), lifetime_stats(),
│   │                            load_flagged() / save_flagged() / toggle_flag()
│   │                            (the flag store itself is common.flags)
│   ├── schedule_store.py        flashcard_schedule.json: load/save, record_rating(),
│   │                            ensure_states() (migration from history)
│   └── review_store.py          the app's adapter over common.journal, plus
│                                flashcard_settings.json
└── ui/
    ├── theme.py                  common.ui.theme + this app's colour vocabulary and the
    │                             few rules for widgets only this app has
    ├── main_window.py            QStackedWidget controller (setup, cards, summary,
    │                             history, browse, reference)
    ├── screens/
    │   ├── setup_screen.py       Daily pull banner, session mode, categories, count,
    │   │                         timer, flagged-only, confidence opt-in
    │   ├── card_screen.py        Card display, reveal, rating buttons, timer, flag toggle,
    │   │                         confidence strip, "what went wrong?" cause row,
    │   │                         "report a problem with this item"
    │   ├── summary_screen.py     Session stats, SM-2 outcome line, review-missed
    │   ├── history_screen.py     Lifetime stats, trend chart, flagged-card list / unflag
    │   └── browse_screen.py      Read-only card browser by category
    └── widgets/
        ├── timer_widget.py       QLabel countdown; turns red at ≤5 s; time_up signal
        └── errata_button.py      Non-blocking "report this card" button over
                                  common.ui.errata_dialog
```

### What comes from `common/`

The Reference screen, the mistake/confidence journal, the flag store, the data-directory
resolution, the palette and the base stylesheet are **not** in this tree any more; they
are the suite-wide implementations in [`common/`](../common/README.md), imported through
the documented shim:

```python
import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import journal
```

`common_path.py` is a verbatim copy of `common/app_shim.py`; it *appends* the repository
root to `sys.path`, so the app's own `config` / `core` / `ui` / `persistence` modules
always win over the repository's. Every module of this app that imports from `common`
imports it first, including `persistence/*.py` (loaded by path, with no conftest, by the
root suite's `tests/test_journal_concurrency.py`).

| Concern | Was | Now |
|---|---|---|
| Docs Reference screen | `ui/screens/reference_screen.py`, 698 lines | `common.ui.reference.ReferenceScreen` |
| Mistake journal + calibration | 477 lines in `persistence/review_store.py` | `common.journal`; the adapter is 380 lines of app-specific glue and docs |
| Flag store | ~90 lines in `persistence/storage.py` | `common.flags` (+ card-bank labels here) |
| Cross-process lock | `journal_sync.py`, 276 lines | `common.locking` |
| Palette + base stylesheet | 170 lines in `ui/theme.py` | `common.ui.theme` (+ 125 lines of this app's own) |
| Data-directory resolution | frozen constants in `config.py` | `common.datadir`, resolved per call |

Two things this app's copies did that the canonical versions do not, and how each was
kept rather than forked:

- **A flag's label and category come from the card bank** (`common.flags` cannot know
  what a card id means). They are *passed in* to `common.flags.toggle_flag`, and
  `persistence/storage.py` keeps the lookup and the first-occurrence de-duplication.
- **`set_mistake_cause` can target one row by timestamp.** The card screen logs a miss
  and then categorises *that* row while the next card is already on screen; the canonical
  helper targets "the newest unresolved row", which is the same row in ordinary use but
  not when one card is missed twice in a session. The adapter keeps the extra precision,
  built out of the canonical load/save inside the canonical lock.

---

## Timer Widget

`TimerWidget` is a `QLabel` subclass driven by a `QTimer`. It is hidden when
`timer_secs = 0`. At each tick it decrements the display and changes colour to red
when ≤ 5 seconds remain. On expiry it emits `time_up` and the card automatically
reveals (same as clicking "Reveal Answer").

The `time_up` signal is disconnected and reconnected on each new card. PyQt6 raises
`TypeError` when `disconnect()` is called on a signal with no connections (the first
card of a run), so the call is wrapped in `try/except (TypeError, RuntimeError)`.

---

## Configuration (`config.py`)

| Setting | Default | Effect |
|---|---|---|
| `DEFAULT_CARD_COUNT` | 20 | Pre-filled card count on setup screen |
| `DEFAULT_TIMER_SECS` | 0 | Pre-filled timer (0 = no timer) |
| `data_dir()` | `~/.local/share/quantum-study` | History / flag / schedule / journal directory |
| `history_file()` | `<data dir>/flashcard_history.json` | Session history (read by coach.py / dashboard.py) |
| `flagged_file()` | `<data dir>/flagged_cards.json` | Flag-for-review entries (legacy name, read by coach.py) |
| `schedule_file()` | `<data dir>/flashcard_schedule.json` | SM-2 schedule (this app only) |
| `mistakes_file()` | `<data dir>/mistakes.json` | Mistake journal (shared with the suite) |
| `confidence_file()` | `<data dir>/confidence.json` | Confidence calibration (shared with the suite) |
| `settings_file()` | `<data dir>/flashcard_settings.json` | This app's preferences (confidence opt-out) |

These are **functions, not constants**: every one resolves
`QUANTUM_STUDY_DATA_DIR` through `common.datadir` at the moment it is called (blank means
no override, `~` is expanded), so setting the variable moves every file this app touches,
at any point, in any process — handy for tests and experiments that must not touch your
real history. The file names themselves come from
`common.datadir.APP_FILES["flashcard-drill"]`, which is where the suite records the names
`coach.py` and `dashboard.py` parse.

---

## Data Persistence

Six files live in the data directory. The first two are shared with `dashboard.py` /
`coach.py` and their schemas are frozen; `mistakes.json` and `confidence.json` are shared
with the other nine apps in the suite; the last two belong to this app alone. **No
schema changed in the migration to `common/`** — only how the files are written:

- **`flashcard_history.json`** — a JSON list; one entry per completed session with
  `total`, `got_it`, `unsure`, `missed`, `timestamp` (epoch seconds) and `results`, a
  list of `{card_id, category, rating, elapsed_secs}` per card (`elapsed_secs` is the
  show-to-rate time and feeds the session-length estimate). Sessions with no rated
  cards are never written.
- **`flagged_cards.json`** — a JSON list of flag entries in the suite-wide shape
  `{"id", "label", "category", "app": "flashcard-drill", "timestamp"}` (the file name is
  the legacy one `coach.py --review` knows about; `label` is the card front). Flagging is
  a toggle: flagging an already-flagged card removes its entry. Older files that hold bare
  id strings are still read and are upgraded on the next write. The Card screen writes it
  after a reveal, the History screen's *Unflag* buttons remove entries, and *Show Flagged
  Only* on the Setup screen reads it.

- **`flashcard_schedule.json`** — the SM-2 schedule, written only by this app:

  ```json
  {
    "alg_grover_iterations": {
      "n": 3,
      "ef": 2.5,
      "interval_days": 15,
      "due_iso": "2026-10-01",
      "last_seen_iso": "2026-09-16",
      "lapses": 1
    }
  }
  ```

  One entry per card that has ever been rated; cards with no entry are "new". It is
  written after **every** rating (atomically, via a temp file plus `os.replace`), so an
  abandoned session still keeps the reviews you did. A missing, unreadable or corrupt
  entry degrades to "this card is new" instead of raising — scheduling never interrupts a
  drill.

- **`mistakes.json`** — the suite-wide **mistake journal**, a JSON list of

  ```json
  {
    "id": "pauli_xyx",
    "app": "flashcard-drill",
    "category": "Pauli Matrices",
    "question": "XYX = ?",
    "your_answer": "Self-rated: Missed (no recall)",
    "correct_answer": "-Y",
    "cause": "knew_but_slipped",
    "note": "little-endian slip again",
    "timestamp": 1790169677.507137,
    "resolved": false
  }
  ```

  `id` is the card id, `category` the card category, and `cause` is one of `misread`,
  `didnt_know`, `knew_but_slipped`, `confused`, `out_of_time`, `other` — or `null`, meaning
  "logged but not yet categorised" (what you get when you skip the row). The three text
  fields are collapsed to one line and clipped to 200 characters. One entry is appended per
  miss, so repeats are separate events; answering the card *Got it* later sets `resolved`
  on every open entry for that `app` + `id`. A miss on the very last card of a session is
  logged but cannot show its row (the summary screen takes over), so it stays
  uncategorised.

- **`confidence.json`** — the suite-wide **calibration log**, a JSON list of

  ```json
  {
    "id": "pauli_xyx",
    "app": "flashcard-drill",
    "category": "Pauli Matrices",
    "confidence": 4,
    "correct": false,
    "timestamp": 1790169677.506926
  }
  ```

  `confidence` is 1 = guessing … 4 = certain, recorded before the reveal; `correct` is
  `true` only for a *Got it* rating. A row is written only when you actually picked a
  confidence. `confidently_wrong()` returns the `confidence >= 3 and not correct` rows —
  the unknown unknowns — and `calibration_summary()` gives per-level accuracy.

- **`flashcard_settings.json`** — `{"confidence_prompt": true}`; written by *Don't ask* on
  the card screen and by the Setup screen's *Self-assessment* tick box.

Both shared files carry every app's rows, and both are written by `common.journal`: the
whole read-modify-write runs under an `fcntl.flock` on a `<file>.lock` sidecar (so two
apps open at once cannot drop each other's rows), the read happens *inside* the lock, and
every row this app does not own is put back exactly as it was read, unknown keys included.
Both tolerate a missing, unreadable, corrupt or partially malformed file by starting fresh
and skipping unusable rows, and neither can raise into a drill — a failed write simply
means that one entry was not recorded. Growth is capped at 2000 mistakes and 5000
confidence rows, and **only this app's own rows are ever dropped** to stay under the cap.

Three details of the shared store differ from this app's pre-migration copy, all of them
the canonical choices recorded in [`common/README.md` §3](../common/README.md):

- a cause is case-normalised (`"Misread"` matches) instead of being discarded;
- a note keeps its line breaks and has its own 500-character cap (the one-line fields are
  still collapsed and clipped to 200);
- a confidence rating outside 1–4 records **nothing** instead of being clamped into range
  — a clamped rating is one the learner never gave.

### Versioning, migration and backups

Every file above is written through `common.schema`, which adds three things and changes
none of the formats:

- **A version sidecar.** `mistakes.json` gets `mistakes.json.schema.json`:
  `{"file", "kind", "schema", "written_by", "updated"}`. It is a *sidecar* rather than a
  key in the data because `coach.py` and `dashboard.py` require the top level of these
  files to be a plain JSON list — a `{"schema": 1, "rows": […]}` wrapper would make them
  read the journal as empty. A file with no sidecar (anything written before this) is
  read as v1, and merely reading it never rewrites it.
- **Forward migration.** When a format does change, the registered migration runs on
  read, in memory; the file is only rewritten the next time something writes it, and is
  stamped then.
- **Refusal instead of corruption.** A file whose sidecar says it was written by a newer
  build is never overwritten with this build's narrower view of it. `save_session` raises
  (the summary screen already reports "this session could not be saved"), the journal
  helpers return "nothing happened" and record the reason in
  `review_store.last_write_error()`, and the flag write surfaces it on the flag button.
- **Rotating backups.** Before the *first* write of each session to a file, its current
  contents are copied to `<file>.bak`, ageing `.bak` → `.bak.1` → `.bak.2`. Three
  generations, one backup per session (not per write), best-effort:
  `common.schema.restore_backup(path)` puts one back.

**Migration.** The first run that has history but no schedule replays
`flashcard_history.json` through the scheduler in timestamp order, at the dates the
sessions actually happened: a card answered "Got it" twice a month ago comes back with
`n = 2`, a 6-day interval, and a due date that has already passed (so it is due now).
History is only read, never rewritten, and the derived schedule is saved once. With no
history at all, nothing is written and the setup screen keeps *Free drill* as the default.

History is never automatically deleted.

---

## Adding New Cards

Add a new Python file inside the appropriate `cards/<category>/` directory, defining a
single module-level `CARD`:

```python
from core.models import Flashcard

CARD = Flashcard(
    id="unique_id",
    category="Category Name",
    front="Question text or concept name",
    back="Answer or definition",
)
```

`cards/__init__.py` auto-discovers every card file, so no registration step is needed.
The SRS system will automatically include the new cards in future sessions. If you
rename a card's `id`, any old ID left in `flagged_cards.json` shows up on the History
screen as "card no longer exists" so it can be unflagged.

---

## Tests

```bash
cd flashcard-drill && python -m pytest
```

Offscreen Qt (`QT_QPA_PLATFORM=offscreen`) and a throwaway `QUANTUM_STUDY_DATA_DIR` are
set by `tests/conftest.py`, so the suite never touches your real history.

| File | Covers |
|---|---|
| `test_scheduler.py` | the SM-2 maths: the `1, 6, 15, 37, 92` ladder, lapses, the `EF` floor/ceiling, the 365-day cap, rating → grade mapping, the due queue, corrupt-value coercion |
| `test_schedule_simulation.py` | 200 cards over 90 simulated days (fixed seed): bounded backlog, every card eventually scheduled |
| `test_schedule_store.py` | `flashcard_schedule.json` round-trips, migration from history, corrupt / unwritable files |
| `test_due_session.py` | the UI end to end offscreen: due counts, mode defaulting, a *Due today* session, the summary line |
| `test_review_store.py` | the journal / calibration helpers with no Qt: the contract schema field for field, cause validation, 200-char clipping, per-app isolation, corrupt and unwritable files, the atomic write, the growth cap, the opt-out setting |
| `test_review_feedback.py` | the same features driven offscreen: a miss journalled and categorised, skip / Escape / dismiss, confidence taken before the reveal and paired with the grade, *Got it* resolving the entry, the *Don't ask* round trip, keyboard reach and accessible names, and proof that the SM-2 schedule and the frozen history schemas are unchanged |
| `test_schema_versioning.py` | the version sidecar for all six files, an unmarked file read as v1 and left alone, a registered migration applied on read and stamped on write, a newer-than-understood file refused at every call site, and the three-generation backup rotation and restore |
| `test_errata.py` | "report a problem with this item": where it appears, what it knows about the card, Tab + Space reach, the dialog opened rather than `exec()`'d (the drill stays live), the prefilled issue's fields, truncation of a 9 000-character card, dismissal reporting nothing, and the no-browser fallback to the clipboard |
| `test_reference_screen.py` | that the app ships the shared `common.ui.reference` screen with the defaults it wants, and that reading, searching, filtering, cross-references and the window wiring still work |
| `test_persistence.py`, `test_card_flow.py`, `test_history_screen.py`, `test_deck.py`, `test_cards.py`, `test_models.py`, `test_app.py` | history and flags round-tripping, the drill end to end offscreen, the history screen, deck building, the card bank itself |

The suite is 249 tests. The root suite's `tests/test_common_*.py` covers the shared code
this app now uses, and `tests/test_journal_concurrency.py` runs this app's store in
parallel with the other nine to prove no rows are lost.

---

## Known issues (not in this app's tree)

- `flashcard-drill/journal_sync.py` is dead code: nothing in the app imports it any more
  (its replacement is `common.locking`). It cannot be deleted yet because the root suite's
  `tests/test_journal_concurrency.py::test_every_app_ships_the_same_journal_sync` requires
  all ten copies to exist *and* uses **this app's copy as the reference text**. Deleting it
  needs that test updated first (skip the apps that have migrated, and re-base the
  byte-identity check on a copy that still exists).
- `tests/test_common_ui.py::test_the_palette_matches_every_app_it_was_extracted_from`
  greps each `<app>/ui/theme.py` for literal `NAME = "#rrggbb"` lines and asserts it read
  at least 100 of them. Now that the apps import the palette from `common.ui.theme`
  instead of redefining it, it reads none — the assertion has to become "every literal one
  that is still there matches", with no floor.
- `common.journal.trim_own(rows, app, cap)` compares the cap against the **whole file's**
  row count, not this app's share of it, so a data directory dominated by another app's
  rows would trim this app harder than the documented "newest 2000 of your own". It never
  drops another app's row, which is the property that matters, and 2000/5000 is far from
  reach in practice.
- `common.journal` and `common.flags` raise `OSError` out of a write when the data
  directory cannot be created (e.g. a file where a directory should be), which contradicts
  the package's own "nothing raises into a drill" invariant. This app's adapter catches it
  and returns "not written"; the other nine will each need the same guard until it is
  fixed centrally.

# Flashcard Drill

A spaced-repetition flashcard app for quantum computing — the only app in the suite that
requires no API key and no Qiskit. 550 cards across 14 categories, with a real **SM-2
scheduler** (due dates and a daily pull — "23 cards due today"), SRS-weighted free drills,
an optional per-card countdown timer, flag-for-review, an in-app Reference browser for the
shared docs corpus, and full session history.

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
- **Reference browser** — read every chapter of the suite's `docs/` corpus inside the
  app, with chapter filter, full-text search and hideable exercise solutions
- **Browse mode** — read-only view of every card by category
- **Session history** — lifetime totals plus a % Known trend chart
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
6. Click **Start Drill**

In *Due today* mode with nothing due and no new cards left, *Start Drill* is disabled and
its tooltip says when to come back.

Once you have rated a few cards, an "≈ N min" estimate under the card count uses your
median seconds-per-card from past sessions.

Footer buttons: **View History**, **Browse Cards**, **Reference**.

### Card Screen

- The **front** of the card is shown centred in the card frame
- Click **Reveal Answer** (or press Space / Enter, or wait for the timer) to flip the card
- Rate yourself (buttons or keys `1` / `2` / `3`). The card screen keeps keyboard focus
  itself (no button on it can take focus), so the shortcuts work after mouse clicks too
  - **Got it** — you knew the answer confidently
  - **Unsure** — you had partial recall
  - **Missed** — you did not know the answer
- **⚑ Flag for Review** appears after the reveal; it is a toggle — click again to unflag
- **End Session** finishes early (rated cards are still saved; with nothing rated it
  simply returns to Setup and nothing is written)

Repeat until all cards are done; the session summary appears automatically.

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

An in-app browser for the shared study docs (`<repo>/docs/**/*.md` — 58 chapters plus
the README):

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
├── config.py                    APP_NAME, DATA_DIR, HISTORY_FILE, SCHEDULE_FILE, defaults
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
├── persistence/
│   ├── storage.py               save_session(), card_weights(), lifetime_stats(),
│   │                            load_flagged() / save_flagged() / toggle_flag()
│   └── schedule_store.py        flashcard_schedule.json: load/save, record_rating(),
│                                ensure_states() (migration from history)
└── ui/
    ├── theme.py                  Shared dark palette + QSS
    ├── main_window.py            QStackedWidget controller (setup, cards, summary,
    │                             history, browse, reference)
    ├── screens/
    │   ├── setup_screen.py       Daily pull banner, session mode, categories, count,
    │   │                         timer, flagged-only
    │   ├── card_screen.py        Card display, reveal, rating buttons, timer, flag toggle
    │   ├── summary_screen.py     Session stats, SM-2 outcome line, review-missed
    │   ├── history_screen.py     Lifetime stats, trend chart, flagged-card list / unflag
    │   ├── browse_screen.py      Read-only card browser by category
    │   └── reference_screen.py   Docs browser for <repo>/docs/**/*.md
    └── widgets/
        └── timer_widget.py       QLabel countdown; turns red at ≤5 s; time_up signal
```

The Reference screen locates the docs corpus as
`Path(__file__).resolve().parents[3] / "docs"` (i.e. `ui/screens/` → `ui/` →
`flashcard-drill/` → repo root), the same contract used by the other suite apps.

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

| Constant | Default | Effect |
|---|---|---|
| `DEFAULT_CARD_COUNT` | 20 | Pre-filled card count on setup screen |
| `DEFAULT_TIMER_SECS` | 0 | Pre-filled timer (0 = no timer) |
| `DATA_DIR` | `~/.local/share/quantum-study` | History / flag / schedule storage directory |
| `HISTORY_FILE` | `DATA_DIR/flashcard_history.json` | Session history (shared with the suite) |
| `SCHEDULE_FILE` | `DATA_DIR/flashcard_schedule.json` | SM-2 schedule (this app only) |

Set the `QUANTUM_STUDY_DATA_DIR` environment variable to point `DATA_DIR` somewhere else
(the same override `coach.py` honours) — handy for tests and experiments that must not
touch your real history.

---

## Data Persistence

Three files live in `DATA_DIR`; the first two are shared with `dashboard.py` / `coach.py`
and their schemas are frozen:

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
| `test_deck.py`, `test_card_flow.py`, `test_persistence.py`, … | pre-existing deck, flow and persistence coverage |

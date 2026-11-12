# Flashcard Drill

A spaced-repetition flashcard app for quantum computing — the only app in the suite that
requires no API key and no Qiskit. 550 cards across 14 categories, with a real **SM-2
scheduler** (due dates and a daily pull — "23 cards due today"), SRS-weighted free drills,
an optional per-card countdown timer, flag-for-review, a **mistake journal** and
**confidence calibration**, an in-app Reference browser for the shared docs corpus, and full
session history.

Its journal, flag store, data-directory resolution, theme and Reference screen come from
the suite's shared [`quantum_study/common/`](../common/README.md) package, so a fix made once reaches
all ten apps; every file it writes is version-stamped, migrated forward and backed up by
`common.schema`; and a wrong card can be reported from inside the drill as a prefilled
GitHub issue.

## Run

```bash
python launch.py flash                 # from the repository root (or: quantum-study flash)
python -m quantum_study.flashcard_drill
```

Fully offline; it never calls the API.
Setup is covered in [GETTING_STARTED.md](../../GETTING_STARTED.md).

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

## Spaced Repetition

Two independent mechanisms, both fed by the same three ratings:

| | Scheduler (SM-2) | Free-drill weighting |
|---|---|---|
| Question it answers | *when* should this card come back? | *which* cards should this session sample? |
| State | `flashcard_schedule.json` (per card: `n`, `EF`, interval, due date) | derived on the fly from `flashcard_history.json` |
| Used by | *Due today* mode, the due counts on the setup screen | *Free drill* mode |

Every rating updates the schedule, whichever mode you drilled in.

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

## Free-Drill Weighting

Session history is read from `flashcard_history.json` (see Data files) every time
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

## Data files

Written under `~/.local/share/quantum-study/`, or `$QUANTUM_STUDY_DATA_DIR` if set:

| File | Holds |
|---|---|
| `flashcard_history.json` | every finished session; read by `coach.py` and `dashboard.py` |
| `flagged_cards.json` | items you flagged for review (the coach's review queue) |
| `flashcard_schedule.json` | the SM-2 schedule: ease, interval and due date per card |
| `flashcard_settings.json` | preferences |
| `mistakes.json`, `confidence.json` | the mistake journal and the confidence ratings, shared by all ten apps |

## Code and tests

The app is the package `quantum_study/flashcard_drill/`. What it shares with the other nine (the data directory, the journals, the theme, the Reference screen) is in [`quantum_study/common/`](../common/README.md).

```bash
pytest quantum_study/flashcard_drill        # this app's tests
```

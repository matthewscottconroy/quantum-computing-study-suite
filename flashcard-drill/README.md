# Flashcard Drill

A spaced-repetition flashcard app for quantum computing — the only app in the suite that
requires no API key and no Qiskit. 82 cards across 7 categories, with SRS weighting,
optional per-card countdown timer, and full session history.

---

## Features

- **82 cards across 7 categories** — Pauli matrices, gate unitaries, commutators,
  complexity, theorems, quantum information, and quantum algorithms
- **Spaced repetition** — cards you missed recently appear with higher frequency
- **Optional countdown timer** — configurable per session; timer turns red at 5 s
- **Three-way rating** — Got it / Unsure / Missed after each reveal
- **Session history** — cumulative stats and per-session breakdown with bar chart
- **Lifetime stats** — total cards drilled, all-time known percentage
- **Zero external dependencies** — only PyQt6 required

---

## Requirements

```
PyQt6>=6.6
```

Install:
```bash
pip install PyQt6
```

---

## Running

```bash
python main.py
```

No API key, no network connection needed.

---

## Usage

### Setup Screen

1. **Select categories** — all 7 checked by default
2. **Card count** — how many cards to draw this session (default 20)
3. **Timer** — seconds per card (0 = no timer)
4. Click **Start Drill**

### Card Screen

- The **front** of the card is shown centred in the card frame
- Click **Reveal Answer** (or wait for the timer) to flip the card
- The **back** animates in below a divider
- Rate yourself:
  - **Got it** — you knew the answer confidently
  - **Unsure** — you had partial recall
  - **Missed** — you did not know the answer

Repeat until all cards are done; the session summary appears automatically.

### Summary Screen

- Got it / Unsure / Missed counts and percentages
- Bar chart of ratings per category (matplotlib-free; uses Qt bar drawing)
- **Drill again** with the same configuration
- **Back to Setup**

### History Screen

- Per-session table: date, card count, % known
- Lifetime totals at the top
- **Clear history** (with confirmation)

---

## Card Categories and Counts

| Category | Cards | Sample Topics |
|---|---|---|
| Pauli Matrices | 12 | X, Y, Z matrices; eigenvalues; commutation/anticommutation; Bloch sphere axes |
| Gate Unitaries | 15 | H, S, T, CNOT, CZ, SWAP, Toffoli matrices; eigenvalues; decompositions |
| Commutators | 11 | [X,Y], [H,X], [X,Z]; uncertainty principle; commuting observables; Pauli algebra |
| Complexity | 10 | BQP, QMA, PSPACE; oracle separations; Grover optimality; Shor complexity |
| Theorems | 11 | No-cloning, Solovay-Kitaev, Gottesman-Knill, threshold theorem, Eastin-Knill |
| Quantum Information | 11 | Von Neumann entropy, fidelity, trace distance, Holevo bound, channel capacity |
| Algorithms | 12 | Grover speedup, QPE circuit, QFT structure, Shor period-finding, HHL conditions |

**Total: 82 cards**

---

## Spaced Repetition Algorithm

Session history is read from `~/.local/share/quantum-study/flashcard_history.json` on
each launch. The weight for each card is computed as:

```
decay = 0.85    # per-session age factor
ease_map = { got_it: 1.0, unsure: 0.5, missed: 0.0 }

For each session (newest first, with age factor decay^age):
    weighted_ease[card_id] += decay^age × ease_map[rating]
    weighted_count[card_id] += decay^age

ease_score[card_id] = weighted_ease[card_id] / weighted_count[card_id]
weight[card_id] = max(0.1, 1.0 - ease_score[card_id])
```

Cards you got right recently have ease ≈ 1.0 → weight ≈ 0.0 (rarely sampled).
Cards you missed recently have ease ≈ 0.0 → weight ≈ 1.0 (frequently sampled).
Cards with no history have weight 1.0 (equal chance with missed cards).
The minimum weight is 0.1 so no card is permanently excluded.

### Deck Building

`build_deck(config)` in `core/deck.py`:
1. Compute weights for the filtered card pool
2. Draw `k` cards with replacement using `random.choices(pool, weights=weights, k=k)`
3. Deduplicate while preserving the weighted order
4. If fewer unique cards were drawn than requested, fill from a uniform shuffle of the
   remaining unselected cards

---

## Architecture

```
flashcard-drill/
├── main.py
├── config.py                    APP_NAME, DATA_DIR, HISTORY_FILE, defaults
├── core/
│   ├── models.py                Flashcard, DrillConfig, Rating, CardResult, SessionStats
│   └── deck.py                  build_deck(config) — SRS-weighted sampling
├── cards/
│   ├── __init__.py              ALL_CARDS list: exports every card from every module
│   ├── pauli_matrices.py        12 cards
│   ├── gate_unitaries.py        15 cards
│   ├── commutators.py           11 cards
│   ├── complexity.py            10 cards
│   ├── theorems.py              11 cards
│   ├── quantum_info.py          11 cards
│   └── algorithms.py            12 cards
├── persistence/
│   └── storage.py               save_session(), card_weights(), lifetime_stats()
└── ui/
    ├── main_window.py            Screen controller (setup → card → summary → history)
    ├── screens/
    │   ├── setup_screen.py       Category selection, card count, timer
    │   ├── card_screen.py        Card display, reveal, rating buttons, timer
    │   ├── summary_screen.py     Session stats
    │   └── history_screen.py     Past sessions table + lifetime stats
    └── widgets/
        └── timer_widget.py       QLabel countdown; turns red at ≤5 s; time_up signal
```

---

## Timer Widget

`TimerWidget` is a `QLabel` subclass driven by a `QTimer`. It is hidden when
`timer_secs = 0`. At each tick it decrements the display and changes colour to red
when ≤ 5 seconds remain. On expiry it emits `time_up` and the card automatically
reveals (same as clicking "Reveal Answer").

The `time_up` signal is disconnected and reconnected on each new card via
`try/except RuntimeError` to avoid PyQt6's signal accumulation bug (PyQt6 does not
expose a `receivers()` method on bound signals, so the try/except pattern is required).

---

## Configuration (`config.py`)

| Constant | Default | Effect |
|---|---|---|
| `DEFAULT_CARD_COUNT` | 20 | Pre-filled card count on setup screen |
| `DEFAULT_TIMER_SECS` | 0 | Pre-filled timer (0 = no timer) |
| `DATA_DIR` | `~/.local/share/quantum-study` | History storage directory |

---

## Data Persistence

Sessions appended to `~/.local/share/quantum-study/flashcard_history.json`. Each entry
records: total cards, got_it count, unsure count, missed count, and per-card results
(card_id, category, rating).

History is never automatically deleted. The History screen provides a manual "Clear
history" button with confirmation.

---

## Adding New Cards

Add a new Python file to `cards/` following this pattern:

```python
from core.models import Flashcard

CARDS = [
    Flashcard(
        id="unique_id",
        category="Category Name",
        front="Question text or concept name",
        back="Answer or definition",
    ),
    ...
]
```

Then export from `cards/__init__.py`:

```python
from cards.your_module import CARDS as _your_cards
ALL_CARDS = [...existing..., *_your_cards]
```

The SRS system will automatically include the new cards in future sessions.

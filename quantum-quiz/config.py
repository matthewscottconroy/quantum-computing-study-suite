"""App-wide constants. Change these to tune behaviour without touching logic."""

# ── Claude ───────────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-sonnet-4-6"
GENERATION_MAX_TOKENS = 900
EVALUATION_MAX_TOKENS = 1300

# ── Session defaults ─────────────────────────────────────────────────────────
DEFAULT_QUESTION_COUNT = 10
MAX_HINT_COUNT = 3
PREVIOUS_QUESTION_DEDUP_WINDOW = 8   # how many past questions Claude sees

# ── Qiskit ───────────────────────────────────────────────────────────────────
CIRCUIT_RENDER_DPI = 120
CIRCUIT_MAX_QUBITS = 6               # keep rendered circuits readable

# ── Scoring ──────────────────────────────────────────────────────────────────
SCORE_CORRECT_THRESHOLD = 7          # score >= this → "Correct"
SCORE_PARTIAL_THRESHOLD = 4          # score >= this → "Partially correct"

# ── UI ───────────────────────────────────────────────────────────────────────
APP_NAME = "Quantum Quiz"
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 650
SCORE_BAR_ANIMATION_MS = 700
COLLAPSIBLE_ANIMATION_MS = 250

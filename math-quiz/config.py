"""App-wide constants."""

from pathlib import Path

# ── Claude ───────────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-sonnet-4-6"
API_KEY_FILE = Path.home() / ".config" / "quantum-study" / "api_key.txt"
GENERATION_MAX_TOKENS = 900
EVALUATION_MAX_TOKENS = 1300

# ── Session defaults ─────────────────────────────────────────────────────────
DEFAULT_QUESTION_COUNT = 10
MAX_HINT_COUNT = 3
PREVIOUS_QUESTION_DEDUP_WINDOW = 8

# ── Scoring ──────────────────────────────────────────────────────────────────
SCORE_CORRECT_THRESHOLD = 7
SCORE_PARTIAL_THRESHOLD = 4

# ── UI ───────────────────────────────────────────────────────────────────────
APP_NAME = "Math for Quantum"
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 650
SCORE_BAR_ANIMATION_MS = 700
COLLAPSIBLE_ANIMATION_MS = 250

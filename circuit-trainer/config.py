"""App-wide constants."""

from pathlib import Path

# ── Claude ───────────────────────────────────────────────────────────────────
CLAUDE_MODEL            = "claude-sonnet-4-6"
CLAUDE_MAX_TOKENS       = 1400
API_KEY_FILE            = Path.home() / ".config" / "quantum-study" / "api_key.txt"

# ── UI ───────────────────────────────────────────────────────────────────────
APP_NAME                = "Circuit Trainer"
WINDOW_MIN_WIDTH        = 1000
WINDOW_MIN_HEIGHT       = 700
SCORE_ANIMATION_MS      = 600

# ── Grading ──────────────────────────────────────────────────────────────────
NUMERIC_TOLERANCE       = 1e-3   # for probability / amplitude comparisons
PHASE_TOLERANCE         = 1e-3   # global phase threshold

# ── Session ──────────────────────────────────────────────────────────────────
DEFAULT_PROBLEM_COUNT   = 12

# ── Sprint mode ──────────────────────────────────────────────────────────────
SPRINT_QUESTION_COUNT   = 10     # questions per sprint
SPRINT_SECONDS          = 60     # countdown per question; timeout = wrong
SPRINT_FLASH_MS         = 900    # right/wrong flash duration before advancing

# ── Circuit rendering ─────────────────────────────────────────────────────────
CIRCUIT_DPI             = 130

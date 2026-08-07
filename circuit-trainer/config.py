"""App-wide constants."""

# ── Claude ───────────────────────────────────────────────────────────────────
CLAUDE_MODEL            = "claude-sonnet-4-6"
CLAUDE_MAX_TOKENS       = 1400

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

# ── Circuit rendering ─────────────────────────────────────────────────────────
CIRCUIT_DPI             = 130

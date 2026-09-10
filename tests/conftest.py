"""Root pytest configuration.

Covers the console tools at the repository root (coach.py, dashboard.py,
launch.py) and tools/verify_docs.py.  Each PyQt app has its own tests/
directory and pytest.ini and is run in a separate pytest process by
tools/run_tests.sh (several apps share top-level package names such as
problems/, core/, ui/).
"""

from __future__ import annotations

import atexit
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"

for _p in (str(TOOLS), str(ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# coach.py resolves its data directory from this variable at import time.
# Point it at a throwaway directory *before* any test module imports coach so
# nothing in this suite can ever read or write ~/.local/share/quantum-study/.
# The directory has to exist before the import, so it cannot be created lazily
# in a fixture; register the cleanup with atexit so it also runs when no test
# executes (--collect-only, an all-deselected -k, a collection error) -- a
# session-scoped fixture would leak the directory in those cases.
_SAFE_DATA_DIR = Path(tempfile.mkdtemp(prefix="quantum-study-tests-"))
os.environ["QUANTUM_STUDY_DATA_DIR"] = str(_SAFE_DATA_DIR)
atexit.register(shutil.rmtree, _SAFE_DATA_DIR, ignore_errors=True)

DAY = 86400.0


def today_local() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def synthetic_payloads(now: float) -> dict[str, list]:
    """One JSON payload per file that coach.py / dashboard.py read.

    Mirrors what each app's persistence layer actually writes (schemas are
    also documented in dashboard.py / coach.py).  Designed so that every app
    has activity today, one QEC category is stale (10 days), and the review
    queue has at least one entry from each source it merges: a contract-shaped
    ``<prefix>_flagged.json`` entry ({id, label, category, app, timestamp}),
    the three legacy bare-id flag files, exam_missed.json, and low-scoring
    math-quiz / quantum-quiz / problem-trainer attempts.
    """
    today = today_local()
    stale_ts = now - 10 * DAY - 3600          # safely > 10 whole days ago
    # circuit-trainer, math-quiz and quantum-quiz store "timestamp" as an
    # ISO-8601 UTC *string* next to a local "date".  coach._session_epoch
    # parses that string; dashboard._session_timestamp / _session_weight do
    # not (float() rejects it) and reach these sessions through the "date"
    # fallback -- the paths every real session of those three apps takes.
    iso_now = datetime.fromtimestamp(now, tz=timezone.utc).isoformat()
    return {
        # -- qec_history / vqa_history --------------------------------------
        "qec_history.json": [
            {"total": 3, "correct": 1, "accuracy": 0.33, "timestamp": now - 60,
             "attempts": [
                 {"problem_id": "qec_stab_01", "category": "stabilizers",
                  "difficulty": "easy", "score": 2, "verdict": "wrong",
                  "hints_used": 1, "elapsed_secs": 40},
                 {"problem_id": "qec_stab_02", "category": "stabilizers",
                  "difficulty": "medium", "score": 3, "verdict": "partial",
                  "hints_used": 0, "elapsed_secs": 55},
                 {"problem_id": "qec_surf_01", "category": "surface code",
                  "difficulty": "hard", "score": 9, "verdict": "correct",
                  "hints_used": 0, "elapsed_secs": 70},
             ]},
            {"total": 1, "correct": 0, "accuracy": 0.0, "timestamp": stale_ts,
             "attempts": [
                 {"problem_id": "qec_dec_01", "category": "decoders",
                  "difficulty": "hard", "score": 4, "verdict": "wrong",
                  "hints_used": 2, "elapsed_secs": 90},
             ]},
        ],
        "vqa_history.json": [
            {"total": 2, "correct": 1, "accuracy": 0.5, "timestamp": now - 90,
             "attempts": [
                 {"problem_id": "vqa_ans_01", "category": "ansatz",
                  "difficulty": "easy", "score": 3, "verdict": "wrong",
                  "hints_used": 0, "elapsed_secs": 30},
                 {"problem_id": "vqa_grad_01", "category": "gradients",
                  "difficulty": "medium", "score": 8, "verdict": "correct",
                  "hints_used": 0, "elapsed_secs": 45},
             ]},
        ],
        # -- flashcard_history ------------------------------------------------
        "flashcard_history.json": [
            {"total": 3, "got_it": 1, "unsure": 1, "missed": 1,
             "timestamp": now - 120,
             "results": [
                 {"card_id": "fc_t1", "category": "hardware", "rating": "missed"},
                 {"card_id": "fc_t2", "category": "hardware", "rating": "unsure"},
                 {"card_id": "fc_grover", "category": "algorithms",
                  "rating": "got_it"},
             ]},
        ],
        # -- trainer_history (Circuit Trainer; "date" + ISO-string timestamp) --
        "trainer_history.json": [
            {"date": today, "timestamp": iso_now, "total": 2, "correct": 1,
             "accuracy": 0.5,
             "attempts": [
                 {"problem_id": "ct_bell_01", "category": "entanglers",
                  "difficulty": "easy", "score": 6, "elapsed_secs": 30},
                 {"problem_id": "ct_ghz_02", "category": "entanglers",
                  "difficulty": "hard", "score": 4, "elapsed_secs": 75},
             ]},
        ],
        # -- math_history / quiz_history ("date" + ISO-string timestamps) -----
        "math_history.json": [
            {"date": today, "timestamp": iso_now, "answered": 3,
             "average_score": 4.3,
             "records": [
                 {"question_id": "mq_eig_01", "subject": "Linear Algebra",
                  "topic": "eigenvalues", "score": 2, "elapsed_seconds": 40,
                  "timestamp": iso_now},
                 {"question_id": "mq_eig_02", "subject": "Linear Algebra",
                  "topic": "eigenvalues", "score": 2, "elapsed_seconds": 50,
                  "timestamp": iso_now},
                 {"question_id": "mq_int_01", "subject": "Calculus",
                  "topic": "integrals", "score": 9, "elapsed_seconds": 35,
                  "timestamp": iso_now},
             ]},
        ],
        "quiz_history.json": [
            {"date": today, "timestamp": iso_now, "answered": 2,
             "average_score": 5.0,
             "records": [
                 {"question_id": "qq_grover_01", "subject": "Algorithms",
                  "topic": "grover", "score": 1, "elapsed_seconds": 60,
                  "timestamp": iso_now},
                 {"question_id": "qq_shor_01", "subject": "Algorithms",
                  "topic": "shor", "score": 9, "elapsed_seconds": 45,
                  "timestamp": iso_now},
             ]},
        ],
        # -- paper_history (no timestamp at all) ------------------------------
        "paper_history.json": [
            {"title": "Shor 1994", "total": 5, "average": 6.0,
             "scores": [4, 6, 8, 6, 6]},
        ],
        # -- dojo_history ------------------------------------------------------
        "dojo_history.json": [
            {"timestamp": now - 150, "total": 3, "passed": 1,
             "attempts": [
                 {"kata_id": "k1", "section": "Primitives", "passed": False,
                  "tries": 2},
                 {"kata_id": "k2", "section": "Primitives", "passed": True,
                  "tries": 1},
                 {"kata_id": "k3", "section": "Transpiler", "passed": False,
                  "tries": 3},
             ]},
        ],
        # -- exam_history ------------------------------------------------------
        "exam_history.json": [
            {"timestamp": now - 3600, "mode": "full", "total": 68,
             "correct": 40, "duration_secs": 5000,
             "sections": {
                 "Primitives": {"total": 10, "correct": 3},
                 "Circuits": {"total": 20, "correct": 18},
                 "Transpiler": {"total": 38, "correct": 19},
             }},
            {"timestamp": now - 7200, "mode": "sprint", "total": 10,
             "correct": 5, "duration_secs": 600,
             "sections": {"Primitives": {"total": 10, "correct": 5}}},
        ],
        # -- problems_history --------------------------------------------------
        "problems_history.json": [
            {"timestamp": now - 300, "total": 2, "avg_score": 4.5,
             "attempts": [
                 {"problem_id": "p_grover_1", "kind": "problem", "score": 3},
                 {"problem_id": "d_qft", "kind": "derivation", "score": 6},
             ]},
        ],
        # -- flagged / missed files read by the coach's review queue ----------
        # Contract shape ({id, label, category, app, timestamp}) as written by
        # quantum-quiz (id = "subject::topic"); the same shape is used by
        # math/trainer/paper/dojo/problems_flagged.json.
        "quiz_flagged.json": [
            {"id": "Algorithms::grover",
             "label": "How many Grover iterations for N = 4, one marked item?",
             "category": "Algorithms", "app": "quantum-quiz",
             "timestamp": now - 500},
        ],
        # Legacy shape: flashcard-drill, qec-trainer and vqa-trainer persist
        # json.dumps(sorted(ids)) -- bare string lists, no timestamps.
        "flagged_cards.json": ["fc_bloch", "fc_t1"],
        "qec_flagged.json": ["qec_steane"],
        "vqa_flagged.json": ["vqa_qaoa"],
        # exam-sim/persistence.record_miss shape; coach reads question_id,
        # section and timestamp, the other keys ride along for fidelity.
        "exam_missed.json": [
            {"question_id": "ex_017", "section": "Primitives",
             "question": "Which primitive returns expectation values?",
             "correct_answer": "Estimator", "chosen": "Sampler",
             "timestamp": now - 3600},
        ],
    }


@pytest.fixture
def now() -> float:
    return time.time()


@pytest.fixture
def payloads(now) -> dict[str, list]:
    return synthetic_payloads(now)


@pytest.fixture
def write_payloads():
    def _write(directory: Path, data: dict[str, list]) -> None:
        for name, payload in data.items():
            (directory / name).write_text(json.dumps(payload), encoding="utf-8")
    return _write


@pytest.fixture
def data_dir(tmp_path, monkeypatch) -> Path:
    """Redirect coach.py and dashboard.py at an empty temporary directory."""
    import coach
    import dashboard

    monkeypatch.setattr(coach, "DATA_DIR", tmp_path)
    monkeypatch.setattr(coach, "STATE_PATH", tmp_path / "coach_state.json")
    monkeypatch.setattr(dashboard, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dashboard, "_FILES",
                        {name: tmp_path / path.name
                         for name, path in dashboard._FILES.items()})
    return tmp_path


@pytest.fixture
def synthetic_dir(data_dir, payloads, write_payloads) -> Path:
    """data_dir populated with a history file for all 10 apps + flag files.

    Flag files: one contract-shaped quiz_flagged.json plus the three legacy
    bare-id files (flagged_cards / qec_flagged / vqa_flagged) and
    exam_missed.json.
    """
    write_payloads(data_dir, payloads)
    return data_dir

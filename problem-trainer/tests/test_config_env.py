"""config.DATA_DIR honours QUANTUM_STUDY_DATA_DIR.

Run in a fresh interpreter (the variable is read at import time), without Qt,
so the check is independent of the in-process monkeypatching every other test
relies on.  Nothing is written: the override directory must not appear.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = Path.home() / ".local" / "share" / "quantum-study"

_PROBE = (
    "import json, config, persistence; "
    "print(json.dumps([str(config.DATA_DIR), str(config.HISTORY_FILE), "
    "str(config.FLAGGED_FILE), str(persistence.HISTORY_FILE), "
    "str(persistence.FLAGGED_FILE)]))"
)


def _probe(**env_override: str) -> tuple[Path, Path, Path, Path, Path]:
    env = {k: v for k, v in os.environ.items() if k != "QUANTUM_STUDY_DATA_DIR"}
    env.update(env_override)
    proc = subprocess.run([sys.executable, "-c", _PROBE], cwd=APP_ROOT, env=env,
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    return tuple(Path(p) for p in json.loads(proc.stdout))    # type: ignore[return-value]


def test_env_var_relocates_data_dir_and_both_files(tmp_path):
    override = tmp_path / "override"
    data_dir, hist, flagged, p_hist, p_flagged = _probe(QUANTUM_STUDY_DATA_DIR=str(override))
    assert data_dir == override
    assert hist == p_hist == override / "problems_history.json"
    assert flagged == p_flagged == override / "problems_flagged.json"
    assert not override.exists(), "importing config/persistence must not create the directory"


def test_default_is_the_shared_suite_directory():
    data_dir, hist, flagged, *_ = _probe()
    assert data_dir == DEFAULT_DIR
    assert hist == DEFAULT_DIR / "problems_history.json"
    assert flagged == DEFAULT_DIR / "problems_flagged.json"


def test_empty_env_var_falls_back_to_default():
    data_dir, *_ = _probe(QUANTUM_STUDY_DATA_DIR="")
    assert data_dir == DEFAULT_DIR

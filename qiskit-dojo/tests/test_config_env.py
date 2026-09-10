"""config.py resolves every data path from QUANTUM_STUDY_DATA_DIR.

Each case runs in a fresh interpreter (config computes its constants at
import time) from a foreign cwd, and asserts nothing is created on import.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
_KEYS = ("DATA_DIR", "HISTORY_FILE", "FLAGGED_FILE")
_PROBE = (
    "import config, json; "
    f"print(json.dumps({{k: str(getattr(config, k)) for k in {_KEYS!r}}}))"
)


def _resolve(**overrides: str) -> dict[str, Path]:
    env = {k: v for k, v in os.environ.items() if k != "QUANTUM_STUDY_DATA_DIR"}
    env["PYTHONPATH"] = str(APP_ROOT)
    env.update(overrides)
    proc = subprocess.run([sys.executable, "-c", _PROBE], cwd="/", env=env,
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    return {k: Path(v) for k, v in json.loads(proc.stdout).items()}


def test_override_moves_every_path(tmp_path):
    target = tmp_path / "qs-data"
    got = _resolve(QUANTUM_STUDY_DATA_DIR=str(target))
    assert got["DATA_DIR"] == target
    assert got["HISTORY_FILE"] == target / "dojo_history.json"
    assert got["FLAGGED_FILE"] == target / "dojo_flagged.json"
    assert not target.exists(), "importing config must not create the data dir"


def test_unset_falls_back_to_xdg_default_under_home(tmp_path):
    got = _resolve(HOME=str(tmp_path))
    assert got["DATA_DIR"] == tmp_path / ".local" / "share" / "quantum-study"
    assert got["HISTORY_FILE"].parent == got["DATA_DIR"]
    assert got["FLAGGED_FILE"].parent == got["DATA_DIR"]


def test_blank_override_is_ignored(tmp_path):
    got = _resolve(HOME=str(tmp_path), QUANTUM_STUDY_DATA_DIR="   ")
    assert got["DATA_DIR"] == tmp_path / ".local" / "share" / "quantum-study"


def test_tilde_is_expanded(tmp_path):
    got = _resolve(HOME=str(tmp_path), QUANTUM_STUDY_DATA_DIR="~/my-study")
    assert got["DATA_DIR"] == tmp_path / "my-study"
    assert got["FLAGGED_FILE"] == tmp_path / "my-study" / "dojo_flagged.json"

"""config.py resolves every data path from QUANTUM_STUDY_DATA_DIR.

Each case runs in a fresh interpreter (config reads the variable once, at
import time) from a foreign cwd, and asserts importing creates nothing.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
_KEYS = ("DATA_DIR", "HISTORY_FILE", "FLAGGED_FILE", "MISTAKES_FILE",
         "CONFIDENCE_FILE", "SETTINGS_FILE")
_PROBE = (
    "import json, config, persistence; "
    f"d = {{k: str(getattr(config, k)) for k in {_KEYS!r}}}; "
    "d['P_HISTORY'] = str(persistence.HISTORY_FILE); "
    "d['P_FLAGGED'] = str(persistence._FLAGGED_FILE); "
    "d['P_MISTAKES'] = str(persistence.MISTAKES_FILE); "
    "d['P_CONFIDENCE'] = str(persistence.CONFIDENCE_FILE); "
    "d['P_SETTINGS'] = str(persistence.SETTINGS_FILE); "
    "print(json.dumps(d))"
)


def _resolve(**overrides: str) -> dict[str, Path]:
    env = {k: v for k, v in os.environ.items() if k != "QUANTUM_STUDY_DATA_DIR"}
    env["PYTHONPATH"] = str(APP_ROOT)
    env.update(overrides)
    proc = subprocess.run([sys.executable, "-c", _PROBE], cwd="/", env=env,
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    return {k: Path(v) for k, v in json.loads(proc.stdout).items()}


def test_override_moves_every_path(tmp_path):
    target = tmp_path / "qs-data"
    got = _resolve(QUANTUM_STUDY_DATA_DIR=str(target))
    assert got["DATA_DIR"] == target
    assert got["HISTORY_FILE"] == got["P_HISTORY"] == target / "vqa_history.json"
    assert got["FLAGGED_FILE"] == got["P_FLAGGED"] == target / "vqa_flagged.json"
    assert got["MISTAKES_FILE"] == got["P_MISTAKES"] == target / "mistakes.json"
    assert got["CONFIDENCE_FILE"] == got["P_CONFIDENCE"] == target / "confidence.json"
    assert got["SETTINGS_FILE"] == got["P_SETTINGS"] == target / "vqa_settings.json"
    assert not target.exists(), "importing config/persistence must not create the dir"


def test_unset_falls_back_to_the_shared_suite_directory(tmp_path):
    got = _resolve(HOME=str(tmp_path))
    default = tmp_path / ".local" / "share" / "quantum-study"
    assert got["DATA_DIR"] == default
    assert all(got[k].parent == default for k in _KEYS if k != "DATA_DIR")


def test_blank_override_is_ignored(tmp_path):
    got = _resolve(HOME=str(tmp_path), QUANTUM_STUDY_DATA_DIR="   ")
    assert got["DATA_DIR"] == tmp_path / ".local" / "share" / "quantum-study"


def test_tilde_is_expanded(tmp_path):
    got = _resolve(HOME=str(tmp_path), QUANTUM_STUDY_DATA_DIR="~/my-study")
    assert got["DATA_DIR"] == tmp_path / "my-study"
    assert got["MISTAKES_FILE"] == tmp_path / "my-study" / "mistakes.json"

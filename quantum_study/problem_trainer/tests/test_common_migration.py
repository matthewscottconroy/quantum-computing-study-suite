"""What problem-trainer takes from ``quantum_study.common`` and what stays its own.

The shared journal, flag store, data directory, theme and Reference screen
must be the shared implementations, not private copies that drifted; the
app's own vocabulary (categories, colours, file names) must survive.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import quantum_study.common.ui.reference as shared_ref
import quantum_study.common.ui.theme as shared_theme
import quantum_study.common.ui.widgets as shared_widgets
from quantum_study.problem_trainer import persistence
from quantum_study.common import datadir, errata, flags, journal, schema

APP_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent.parent
APP = "problem-trainer"


def _run(code: str, **env_override: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env.update(env_override)
    return subprocess.run([sys.executable, "-c", code], cwd=APP_ROOT, env=env,
                          capture_output=True, text=True, timeout=180)



# ---------------------------------------------------------------------------
# No second copy of anything common/ owns
# ---------------------------------------------------------------------------

def test_the_journal_vocabulary_is_commons_object_not_a_copy():
    assert persistence.MISTAKE_CAUSES is journal.MISTAKE_CAUSES
    assert persistence.MISTAKE_KEYS is journal.MISTAKE_KEYS
    assert persistence.CONFIDENCE_KEYS is journal.CONFIDENCE_KEYS
    assert persistence.CONFIDENCE_LABELS is journal.CONFIDENCE_LABELS
    assert persistence.normalize_cause is not None
    assert persistence.TEXT_FIELD_MAX == journal.TEXT_MAX


def test_the_ui_cause_and_confidence_lists_are_generated_from_the_contract():
    from quantum_study.problem_trainer.ui.widgets.study_journal import CONFIDENCE_LEVELS, MISTAKE_CAUSE_LABELS

    assert [c for c, _ in MISTAKE_CAUSE_LABELS] == list(journal.MISTAKE_CAUSES)
    assert [lv for lv, _ in CONFIDENCE_LEVELS] == list(journal.CONFIDENCE_LEVELS)
    assert [text for _, text in CONFIDENCE_LEVELS] == [
        journal.CONFIDENCE_LABELS[lv] for lv in journal.CONFIDENCE_LEVELS]


def test_the_palette_is_commons_and_the_stylesheet_extends_it():
    from quantum_study.problem_trainer.ui import theme

    for name in ("BG", "SURFACE", "SURFACE2", "BORDER", "ACCENT", "ACCENT2",
                 "TEXT", "TEXT_MUTED", "SUCCESS", "WARNING", "ERROR", "PARTIAL"):
        assert getattr(theme, name) == getattr(shared_theme, name), name
    assert theme.QSS.startswith(shared_theme.QSS)     # base first, app rules after
    assert "QPushButton#flag" in theme.QSS            # this app's own rule
    assert "QPushButton#flag" not in shared_theme.QSS
    assert theme.TOPIC_COLORS                          # app vocabulary stays here


def test_the_reference_screen_is_the_shared_one():
    from quantum_study.problem_trainer.ui.screens.reference_screen import ReferenceScreen

    assert issubclass(ReferenceScreen, shared_ref.ReferenceScreen)
    assert ReferenceScreen is not shared_ref.ReferenceScreen
    # The module re-exports, never redefines, the corpus helpers.
    from quantum_study.problem_trainer.ui.screens import reference_screen as mod
    for name in ("docs_root", "scan_docs", "read_title", "pretty_chapter",
                 "prepare_markdown", "ALL_CHAPTERS", "DocEntry"):
        assert getattr(mod, name) is getattr(shared_ref, name), name


def test_the_loading_overlay_is_commons_and_the_local_copy_is_gone():
    from quantum_study.problem_trainer.ui.screens import problem_screen

    assert problem_screen.LoadingOverlay is shared_widgets.LoadingOverlay
    assert not (APP_ROOT / "ui" / "widgets" / "loading_overlay.py").exists()
    # …and the shared one has the hide_overlay() the plain copies lacked.
    assert hasattr(shared_widgets.LoadingOverlay, "hide_overlay")


def test_the_data_dir_rule_is_commons_and_the_file_names_are_registered():
    assert persistence.data_dir() == datadir.data_dir()
    assert datadir.APP_FILES[APP] == {
        "history": "problems_history.json",
        "flagged": "problems_flagged.json",
        "settings": "problems_settings.json",
    }
    assert persistence.history_path().name == "problems_history.json"
    assert persistence.flagged_path() == flags.flagged_path(APP)
    assert persistence.mistakes_path() == journal.mistakes_path()
    assert persistence.confidence_path() == journal.confidence_path()
    assert persistence.settings_path().name == "problems_settings.json"


def test_this_app_is_known_to_the_shared_errata_and_schema_registries():
    assert APP in errata.APP_ITEM_PATHS
    assert errata.APP_ITEM_PATHS[APP] == "quantum_study/problem_trainer/problems/"
    for kind in ("mistakes", "confidence", "flagged", "history", "settings"):
        assert schema.get(kind).version >= 1


# ---------------------------------------------------------------------------
# A blank / tilde data-dir override, which this app's own copy got wrong
# ---------------------------------------------------------------------------

def test_a_blank_override_is_no_override(monkeypatch):
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", "   ")
    assert persistence.data_dir() == datadir.default_data_dir()


def test_an_unexpanded_tilde_override_is_expanded(monkeypatch):
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", "~/scratch-quantum")
    resolved = persistence.data_dir()
    assert resolved == Path.home() / "scratch-quantum"
    assert "~" not in str(resolved)
    assert not resolved.exists(), "resolving a path must never create it"

"""This app is wired to ``common/`` — and has no second copy of what is there.

The point of the shared package is that a cross-cutting fix lands once.  That
only holds while nobody quietly re-forks a helper here, so these tests assert
identity (``is``), not equality, wherever the app is supposed to be *using*
common rather than agreeing with it.

They also pin the import shim in the three modes that matter — running the app
as a script, running this suite, and loading ``persistence.py`` by path with
nothing but the app directory on ``sys.path``, which is what the repository's
``tests/test_journal_concurrency.py`` does to every app.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

import common.ui.reference as shared_ref
import common.ui.theme as shared_theme
import common.ui.widgets as shared_widgets
import persistence
from common import datadir, errata, flags, journal, schema

APP_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent
APP = "problem-trainer"


def _run(code: str, **env_override: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env.update(env_override)
    return subprocess.run([sys.executable, "-c", code], cwd=APP_ROOT, env=env,
                          capture_output=True, text=True, timeout=180)


# ---------------------------------------------------------------------------
# The import shim
# ---------------------------------------------------------------------------

def test_the_shim_is_the_unedited_copy_of_the_canonical_one():
    """common/README.md: copy app_shim.py verbatim, do not edit it."""
    ours = (APP_ROOT / "common_path.py").read_text(encoding="utf-8")
    canonical = (REPO_ROOT / "common" / "app_shim.py").read_text(encoding="utf-8")
    assert ours == canonical


def test_the_shim_appends_so_a_root_module_can_never_shadow_an_app_module():
    """The repo root holds tests/, tools/, coach.py: prepending it would win."""
    import common_path as shim

    assert shim.ROOT == REPO_ROOT
    assert str(REPO_ROOT) in sys.path
    assert sys.path.index(str(REPO_ROOT)) > sys.path.index(str(APP_ROOT))


def test_persistence_imports_standalone_by_path_with_only_the_app_dir_on_syspath():
    """What tests/test_journal_concurrency.py does to every app, verbatim."""
    code = (
        "import importlib.util, sys, json\n"
        f"sys.path.insert(0, {str(APP_ROOT)!r})\n"
        f"spec = importlib.util.spec_from_file_location('store_pt', {str(APP_ROOT / 'persistence.py')!r})\n"
        "m = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(m)\n"
        "m.log_mistake('probe', 'Gates', 'q', 'a', 'b')\n"
        "m.log_confidence('probe', 'Gates', 3, False)\n"
        "print(json.dumps([e['id'] for e in m.app_mistakes()]))\n"
    )
    proc = _run(code, QUANTUM_STUDY_DATA_DIR=os.environ["QUANTUM_STUDY_DATA_DIR"]
                if "QUANTUM_STUDY_DATA_DIR" in os.environ else "")
    assert proc.returncode == 0, proc.stderr
    assert "probe" in json.loads(proc.stdout.strip().splitlines()[-1])


def test_the_app_starts_as_a_script_with_no_api_key(tmp_path):
    """`cd problem-trainer && python main.py` — the shim's first mode."""
    code = (
        "import main, config\n"
        "from PyQt6.QtWidgets import QApplication\n"
        "app = QApplication([])\n"
        "main.theme.apply(app)\n"
        "w = main.MainWindow()\n"
        "print('OK', w.windowTitle() == config.WINDOW_TITLE)\n"
    )
    env = {"QUANTUM_STUDY_DATA_DIR": str(tmp_path / "data")}
    env["ANTHROPIC_API_KEY"] = ""
    proc = _run(code, **env)
    assert proc.returncode == 0, proc.stderr
    assert "OK True" in proc.stdout


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
    from ui.widgets.study_journal import CONFIDENCE_LEVELS, MISTAKE_CAUSE_LABELS

    assert [c for c, _ in MISTAKE_CAUSE_LABELS] == list(journal.MISTAKE_CAUSES)
    assert [lv for lv, _ in CONFIDENCE_LEVELS] == list(journal.CONFIDENCE_LEVELS)
    assert [text for _, text in CONFIDENCE_LEVELS] == [
        journal.CONFIDENCE_LABELS[lv] for lv in journal.CONFIDENCE_LEVELS]


def test_the_palette_is_commons_and_the_stylesheet_extends_it():
    from ui import theme

    for name in ("BG", "SURFACE", "SURFACE2", "BORDER", "ACCENT", "ACCENT2",
                 "TEXT", "TEXT_MUTED", "SUCCESS", "WARNING", "ERROR", "PARTIAL"):
        assert getattr(theme, name) == getattr(shared_theme, name), name
    assert theme.QSS.startswith(shared_theme.QSS)     # base first, app rules after
    assert "QPushButton#flag" in theme.QSS            # this app's own rule
    assert "QPushButton#flag" not in shared_theme.QSS
    assert theme.TOPIC_COLORS                          # app vocabulary stays here


def test_the_reference_screen_is_the_shared_one():
    from ui.screens.reference_screen import ReferenceScreen

    assert issubclass(ReferenceScreen, shared_ref.ReferenceScreen)
    assert ReferenceScreen is not shared_ref.ReferenceScreen
    # The module re-exports, never redefines, the corpus helpers.
    from ui.screens import reference_screen as mod
    for name in ("docs_root", "scan_docs", "read_title", "pretty_chapter",
                 "prepare_markdown", "ALL_CHAPTERS", "DocEntry"):
        assert getattr(mod, name) is getattr(shared_ref, name), name


def test_the_loading_overlay_is_commons_and_the_local_copy_is_gone():
    from ui.screens import problem_screen

    assert problem_screen.LoadingOverlay is shared_widgets.LoadingOverlay
    assert not (APP_ROOT / "ui" / "widgets" / "loading_overlay.py").exists()
    # …and the shared one has the hide_overlay() the plain copies lacked.
    assert hasattr(shared_widgets.LoadingOverlay, "hide_overlay")


def test_nothing_in_the_app_imports_journal_sync_any_more():
    """The store is common.journal now; the old module is dead code here."""
    assert not hasattr(persistence, "journal_sync")
    sources = [p for p in APP_ROOT.rglob("*.py")
               if p.name not in ("journal_sync.py", Path(__file__).name)
               and ".pytest_cache" not in p.parts]
    needle = "import " + "journal_sync"          # split: this file names it too
    offenders = [str(p.relative_to(APP_ROOT)) for p in sources
                 if needle in p.read_text(encoding="utf-8")]
    assert not offenders, offenders


def test_journal_sync_is_kept_only_to_satisfy_the_repository_suite():
    """The file stays, byte-identical, until the root suite stops requiring it.

    ``tests/test_journal_concurrency.py::test_every_app_ships_the_same_journal_sync``
    asserts all ten copies exist and match.  That test is not this app's to
    change, so the copy is retained unmodified and simply no longer imported;
    this pins it so a stray edit here cannot fail the repository suite.
    """
    ours = APP_ROOT / "journal_sync.py"
    reference = REPO_ROOT / "flashcard-drill" / "journal_sync.py"
    assert ours.is_file()
    assert ours.read_text(encoding="utf-8") == reference.read_text(encoding="utf-8")


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
    assert errata.APP_ITEM_PATHS[APP] == "problem-trainer/problems/"
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

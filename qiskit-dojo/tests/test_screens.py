"""Offscreen screen tests: kata-screen flag button and run-result guard,
History flagged list + Unflag, Reference browser (discovery, <details>
rewrite, links, anchors, Back), and setup-screen pass-rate refresh.

All persistence goes to ``data_dir``; the run harness is replaced by an
in-process fake except where a real subprocess race is deliberately tested.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest
from PyQt6.QtCore import QObject, Qt, QUrl, pyqtSignal
from PyQt6.QtWidgets import QPushButton

import persistence
from core.models import Kata, KataAttempt, RunResult, SessionStats

APP_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = APP_ROOT.parent / "docs"
PATH_ROLE = Qt.ItemDataRole.UserRole


def _kata(kid: str, title: str = "t", section: str = "Sampler") -> Kata:
    return Kata(id=kid, section=section, title=title, difficulty="beginner",
                prompt="p", starter_code="x = 0\n", test_code="assert x == 1\n",
                solution_code="x = 1\n", hints=["h1", "h2"])


def _pump(qapp, n: int = 3) -> None:
    for _ in range(n):
        qapp.processEvents()


def _button(widget, text: str) -> QPushButton:
    for b in widget.findChildren(QPushButton):
        if b.text() == text:
            return b
    raise AssertionError(f"no button {text!r} in {type(widget).__name__}")


def _wait_for_run(qapp, screen, timeout: float = 60.0) -> None:
    t0 = time.time()
    while screen._run_worker is not None and time.time() - t0 < timeout:
        qapp.processEvents()
        time.sleep(0.02)
    _pump(qapp)
    assert screen._run_worker is None, "harness run did not finish"


class _FakeWorker(QObject):
    """Stands in for RunWorker: same signals, no thread, completes on demand."""
    finished_run = pyqtSignal(object)
    failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, user_code: str, test_code: str, parent=None) -> None:
        super().__init__(parent)
        self.user_code = user_code
        self.test_code = test_code

    def start(self) -> None:
        pass

    def complete(self, result: RunResult) -> None:
        self.finished_run.emit(result)
        self.finished.emit()

    def crash(self, err: str) -> None:
        self.failed.emit(err)
        self.finished.emit()


# ------------------------------------------------------------------ fixtures

@pytest.fixture
def kata_mod(monkeypatch):
    """kata_screen module with a fake harness worker and non-blocking dialogs."""
    import ui.screens.kata_screen as mod
    monkeypatch.setattr(mod, "RunWorker", _FakeWorker)
    asked: list = []
    monkeypatch.setattr(
        mod.QMessageBox, "question",
        staticmethod(lambda *a, **k: (asked.append(a[1]), mod.QMessageBox.StandardButton.No)[1]),
    )
    mod._asked_for_test = asked
    return mod


@pytest.fixture
def kata_screen(qapp, data_dir, kata_mod):
    screen = kata_mod.KataScreen()
    yield screen
    screen.close(); screen.deleteLater(); _pump(qapp)


@pytest.fixture
def history_screen(qapp, data_dir):
    from ui.screens.history_screen import HistoryScreen
    screen = HistoryScreen()
    yield screen
    screen.close(); screen.deleteLater(); _pump(qapp)


@pytest.fixture
def reference_screen(qapp):
    from ui.screens.reference_screen import ReferenceScreen
    screen = ReferenceScreen()
    screen.resize(1100, 700)
    screen.show()
    _pump(qapp)
    yield screen
    screen.close(); screen.deleteLater(); _pump(qapp)


def _write_flags(data_dir: Path, entries: list[dict]) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "dojo_flagged.json").write_text(json.dumps(entries))


def _entry(kid: str, ts, category: str = "Sampler") -> dict:
    return {"id": kid, "label": kid.upper(), "category": category,
            "app": "qiskit-dojo", "timestamp": ts}


# --------------------------------------------------------------- KataScreen

def test_flag_button_reflects_and_toggles_persisted_state(kata_screen, kata_mod, qapp, data_dir):
    k = _kata("cc_bell_state", title="Build a Bell state", section="Create circuits")
    persistence.toggle_flag(k)                          # flagged "last session"

    kata_screen.show_kata(k, 1, 1)
    assert kata_screen.is_flagged() is True
    assert kata_screen._flag_btn.text() == kata_mod._FLAG_ON_TEXT

    kata_screen._flag_btn.click(); _pump(qapp)          # toggle off
    assert kata_screen.is_flagged() is False
    assert kata_screen._flag_btn.text() == kata_mod._FLAG_OFF_TEXT
    assert json.loads((data_dir / "dojo_flagged.json").read_text()) == []

    kata_screen._flag_btn.click(); _pump(qapp)          # toggle on again
    entries = json.loads((data_dir / "dojo_flagged.json").read_text())
    assert [(e["id"], e["label"], e["category"], e["app"]) for e in entries] == [
        ("cc_bell_state", "Build a Bell state", "Create circuits", "qiskit-dojo")
    ]
    assert set(entries[0]) == {"id", "label", "category", "app", "timestamp"}

    kata_screen.show_kata(_kata("other"), 1, 1)         # state is per kata
    assert kata_screen.is_flagged() is False
    assert kata_screen._flag_btn.text() == kata_mod._FLAG_OFF_TEXT


def test_run_disables_navigation_until_the_result_arrives(kata_screen, kata_mod, qapp):
    s = kata_screen
    s.show_kata(_kata("a"), 1, 2)
    assert s._run_btn.isEnabled() and s._next_btn.isEnabled() and s._end_btn.isEnabled()

    s._run_btn.click(); _pump(qapp)
    worker = s._run_worker
    assert isinstance(worker, _FakeWorker)
    assert s._attempt.tries == 1
    assert s._status_lbl.text() == "Running…"
    assert not s._run_btn.isEnabled()
    assert not s._next_btn.isEnabled()
    assert not s._end_btn.isEnabled()

    completed: list = []
    s.kata_completed.connect(completed.append)
    s._next_btn.click(); s._end_btn.click(); _pump(qapp)    # inert while running
    assert completed == [] and kata_mod._asked_for_test == []

    worker.complete(RunResult(passed=True, output="ok", phase="pass", duration_secs=0.1))
    _pump(qapp)
    assert s._run_worker is None
    assert s._run_btn.isEnabled() and s._next_btn.isEnabled() and s._end_btn.isEnabled()
    assert s._attempt.passed is True and s._attempt.tries == 1
    assert s._status_lbl.text().startswith("✓ PASSED")
    assert s._output_view.toPlainText() == "ok"
    assert s._next_btn.text() == "Next →" and s._next_btn.objectName() == "accent"


def test_stale_result_is_dropped_not_applied_to_next_kata(kata_screen, qapp):
    """Regression for the Run-then-advance race: a result that arrives after
    the screen moved on must not pass the new kata (or mutate the old one)."""
    s = kata_screen
    a, b = _kata("a"), _kata("b")
    s.show_kata(a, 1, 2)
    attempt_a = s._attempt
    s._run_btn.click(); _pump(qapp)
    worker = s._run_worker

    s.show_kata(b, 2, 2)                                # programmatic advance
    assert not s._next_btn.isEnabled()                  # still in flight
    worker.complete(RunResult(passed=True, output="late", phase="pass", duration_secs=0.2))
    _pump(qapp)

    assert s._kata is b
    assert s._attempt.passed is False and s._attempt.tries == 0
    assert s._status_lbl.text() == ""
    assert s._output_view.toPlainText() == ""
    assert s._next_btn.text() == "Skip →" and s._next_btn.objectName() == ""
    assert attempt_a.passed is False and attempt_a.tries == 1
    assert s._run_worker is None and s._next_btn.isEnabled()


def test_stale_harness_failure_is_dropped_too(kata_screen, qapp):
    s = kata_screen
    s.show_kata(_kata("a"), 1, 2)
    s._run_btn.click(); _pump(qapp)
    worker = s._run_worker
    s.show_kata(_kata("b"), 2, 2)
    worker.crash("boom"); _pump(qapp)
    assert s._status_lbl.text() == "" and s._output_view.toPlainText() == ""
    assert s._run_worker is None and s._run_btn.isEnabled()


def test_harness_failure_on_current_kata_is_shown(kata_screen, qapp):
    s = kata_screen
    s.show_kata(_kata("a"), 1, 1)
    s._run_btn.click(); _pump(qapp)
    s._run_worker.crash("no python"); _pump(qapp)
    assert s._status_lbl.text() == "✗ HARNESS ERROR"
    assert "no python" in s._output_view.toPlainText()
    assert s._attempt.passed is False and s._attempt.tries == 1


def test_next_button_loses_accent_on_the_following_kata(kata_screen, qapp):
    s = kata_screen
    s.show_kata(_kata("a"), 1, 2)
    s._run_btn.click(); _pump(qapp)
    s._run_worker.complete(RunResult(passed=True, output="", phase="pass")); _pump(qapp)
    assert (s._next_btn.text(), s._next_btn.objectName()) == ("Next →", "accent")

    s.show_kata(_kata("b"), 2, 2)
    assert (s._next_btn.text(), s._next_btn.objectName()) == ("Skip →", "")


def test_failed_run_keeps_skip_button(kata_screen, qapp):
    s = kata_screen
    s.show_kata(_kata("a"), 1, 1)
    s._run_btn.click(); _pump(qapp)
    s._run_worker.complete(RunResult(passed=False, output="nope", phase="test_failed",
                                     duration_secs=0.1)); _pump(qapp)
    assert s._status_lbl.text().startswith("✗ TESTS FAILED")
    assert (s._next_btn.text(), s._next_btn.objectName()) == ("Skip →", "")
    assert s._attempt.passed is False and s._attempt.tries == 1


def test_real_harness_pass_updates_current_kata(qapp, data_dir):
    from ui.screens.kata_screen import KataScreen
    s = KataScreen()
    try:
        a = _kata("a")
        s.show_kata(a, 1, 1)
        s._editor.setPlainText(a.solution_code)
        s._run_btn.click()
        assert s._run_worker is not None
        _wait_for_run(qapp, s)
        assert s._attempt.passed is True and s._attempt.tries == 1
        assert s._status_lbl.text().startswith("✓ PASSED")
        assert s._next_btn.text() == "Next →"
    finally:
        s.close(); s.deleteLater(); _pump(qapp)


def test_real_harness_race_run_then_advance(qapp, data_dir):
    """End-to-end with the real subprocess harness (QThread + queued signals):
    a correct solution for kata A whose result lands after the screen advanced
    to kata B must leave B untouched."""
    from ui.screens.kata_screen import KataScreen
    s = KataScreen()
    try:
        a, b = _kata("a"), _kata("b")
        s.show_kata(a, 1, 2)
        s._editor.setPlainText(a.solution_code)
        s._run_btn.click()
        assert s._run_worker is not None and not s._next_btn.isEnabled()
        s.show_kata(b, 2, 2)
        _wait_for_run(qapp, s)
        assert s._kata is b
        assert s._attempt.passed is False and s._attempt.tries == 0
        assert s._status_lbl.text() == "" and s._output_view.toPlainText() == ""
        assert s._next_btn.isEnabled() and s._next_btn.text() == "Skip →"
    finally:
        s.close(); s.deleteLater(); _pump(qapp)


# ------------------------------------------------------------ HistoryScreen

def test_history_lists_flags_newest_first_and_unflag_updates_file_and_ui(
        history_screen, qapp, data_dir):
    h = history_screen
    _write_flags(data_dir, [_entry("old", 1.0), _entry("new", 3.0), _entry("mid", 2.0)])
    h.refresh(); _pump(qapp)
    assert h.flagged_rows() == ["new", "mid", "old"]
    assert h._flag_lbl.text() == "Flagged for review (3)"
    assert len([b for b in h._flag_frame.findChildren(QPushButton) if b.text() == "Unflag"]) == 3

    top_row = h._flag_slot.itemAt(0).widget()          # newest row
    top_row.findChild(QPushButton).click(); _pump(qapp)
    assert h.flagged_rows() == ["mid", "old"]
    assert h._flag_lbl.text() == "Flagged for review (2)"
    on_disk = json.loads((data_dir / "dojo_flagged.json").read_text())
    assert [e["id"] for e in on_disk] == ["old", "mid"]
    assert persistence.flagged_ids() == {"old", "mid"}

    for _ in range(2):
        h._flag_slot.itemAt(0).widget().findChild(QPushButton).click(); _pump(qapp)
    assert h.flagged_rows() == []
    assert h._flag_lbl.text() == "Flagged for review (0)"
    assert json.loads((data_dir / "dojo_flagged.json").read_text()) == []


def test_history_tolerates_non_numeric_timestamps(history_screen, qapp, data_dir):
    _write_flags(data_dir, [_entry("a", 5.0), _entry("b", "2024-01-01"),
                            _entry("c", 7.0), _entry("d", None)])
    history_screen.refresh(); _pump(qapp)              # must not raise TypeError
    assert history_screen.flagged_rows()[:2] == ["c", "a"]
    assert set(history_screen.flagged_rows()[2:]) == {"b", "d"}


def test_history_empty_states(history_screen, qapp, data_dir):
    history_screen.refresh(); _pump(qapp)
    assert history_screen.flagged_rows() == []
    assert history_screen._flag_lbl.text() == "Flagged for review (0)"
    assert not history_screen._empty_lbl.isHidden()

    data_dir.mkdir(parents=True)
    (data_dir / "dojo_flagged.json").write_text("{corrupt")
    history_screen.refresh(); _pump(qapp)
    assert history_screen.flagged_rows() == []


def test_history_footer_style_is_scoped_to_the_bar(history_screen):
    bar = history_screen._footer
    assert bar.objectName() == "footer"
    assert bar.styleSheet().lstrip().startswith("QWidget#footer")
    back = _button(history_screen, "← Back to Setup")
    assert back.objectName() == "accent"
    assert back.styleSheet() == ""                      # nothing cascaded onto it
    fired: list = []
    history_screen.back_requested.connect(lambda: fired.append(True))
    back.click()
    assert fired == [True]


# ---------------------------------------------------------- ReferenceScreen

def test_reference_discovers_every_doc_under_repo_docs(reference_screen, qapp):
    r = reference_screen
    assert r.docs_root == DOCS_ROOT and DOCS_ROOT.is_dir()
    expected = sorted(DOCS_ROOT.rglob("*.md"))
    assert expected, "docs corpus is empty?"

    r.load_all(); _pump(qapp)
    leaves = list(r._iter_leaves())
    assert sorted(Path(l.data(0, PATH_ROLE)) for l in leaves) == expected
    assert r._doc_count == len(expected)
    assert r._count_lbl.text().startswith(f"{len(expected)} chapters")
    assert r.current_path == DOCS_ROOT / "README.md"
    assert r._open_btn.isEnabled()
    # every leaf is titled from its H1 (no prettified-stem fallbacks)
    for leaf in leaves:
        text = Path(leaf.data(0, PATH_ROLE)).read_text(encoding="utf-8")
        h1 = next(line[2:].strip() for line in text.splitlines() if line.startswith("# "))
        assert leaf.text(0) in (h1, "Learning Ladder (README)")

    r.load_all(); _pump(qapp)                           # idempotent: no re-scan
    assert len(list(r._iter_leaves())) == len(expected)


def test_reference_rewrites_details_blocks_in_every_doc(reference_screen):
    r = reference_screen
    with_details = [p for p in sorted(DOCS_ROOT.rglob("*.md"))
                    if "<details>" in p.read_text(encoding="utf-8")]
    assert with_details
    for p in with_details:
        assert r.show_doc(p) is True
        txt = r._browser.toPlainText()
        assert "<details>" not in txt and "<summary>" not in txt and "</details>" not in txt, p
        assert "Solution:" in txt, p
        assert r.current_path == p


def test_reference_fragment_links_scroll_to_headings(reference_screen, qapp):
    r = reference_screen
    doc = next(p for p in sorted(DOCS_ROOT.rglob("*.md"))
               if "\n## Key Formulas" in p.read_text(encoding="utf-8"))
    assert r.show_doc(doc)
    _pump(qapp)
    sb = r._browser.verticalScrollBar()
    assert sb.value() == 0 and sb.maximum() > 0

    r._on_anchor(QUrl("#key-formulas")); _pump(qapp)
    assert sb.value() > 0
    assert r.scroll_to_fragment("Key Formulas") is True   # normalised like GitHub
    assert r.scroll_to_fragment("no-such-heading-xyz") is False
    assert "<a href" not in r._browser.toHtml()            # anchors are not links


def test_reference_relative_missing_and_external_links(reference_screen, qapp, monkeypatch):
    import ui.screens.reference_screen as ref_mod
    opened: list[str] = []
    monkeypatch.setattr(ref_mod.QDesktopServices, "openUrl",
                        staticmethod(lambda url: (opened.append(url.toString()), True)[1]))
    r = reference_screen
    r.load_all(); _pump(qapp)

    chapters = sorted(p for p in DOCS_ROOT.rglob("*.md") if p.parent != DOCS_ROOT)
    src = chapters[0]
    dst = next(p for p in chapters if p.parent != src.parent)
    assert r.show_doc(src)
    rel = os.path.relpath(dst, src.parent)
    r._on_anchor(QUrl(rel)); _pump(qapp)                 # relative .md: in-app
    assert r.current_path == dst
    assert Path(r._tree.currentItem().data(0, PATH_ROLE)) == dst
    assert opened == []

    r._on_anchor(QUrl("does_not_exist.md")); _pump(qapp)  # broken: feedback, no xdg-open
    assert opened == []
    assert r._crumb_lbl.text() == "Link target not found: does_not_exist.md"
    assert r.current_path == dst

    r._on_anchor(QUrl("https://example.com/x")); _pump(qapp)
    assert opened == ["https://example.com/x"]


def test_reference_back_button_and_scoped_top_bar(reference_screen, qapp):
    r = reference_screen
    fired: list = []
    r.back_requested.connect(lambda: fired.append(True))
    r._back_btn.click(); _pump(qapp)
    assert fired == [True]
    assert r._top_bar.objectName() == "refTopBar"
    assert r._top_bar.styleSheet().lstrip().startswith("QWidget#refTopBar")
    assert r._back_btn.styleSheet() == "" and r._open_btn.styleSheet() == ""


def test_reference_missing_docs_root_is_reported(qapp, tmp_path, monkeypatch):
    import ui.screens.reference_screen as ref_mod
    monkeypatch.setattr(ref_mod, "_DOCS_ROOT", tmp_path / "nope")
    r = ref_mod.ReferenceScreen()
    try:
        r.load_all(); _pump(qapp)
        assert "Docs folder not found" in r._browser.toPlainText()
        assert r._count_lbl.text() == "0 chapters"
        assert list(r._iter_leaves()) == []
    finally:
        r.close(); r.deleteLater(); _pump(qapp)


# -------------------------------------------------------------- SetupScreen

def _one_pass(section: str = "Sampler") -> SessionStats:
    return SessionStats(attempts=[KataAttempt(_kata("k", section=section), passed=True, tries=1)])


def test_setup_rates_refresh_without_restart(qapp, data_dir):
    from ui.screens.setup_screen import SetupScreen
    s = SetupScreen()
    try:
        assert s.section_rate_text("Sampler") == "—"
        assert s._rate_bars["Sampler"].value() == 0
        persistence.save_session(_one_pass("Sampler"))
        assert s.section_rate_text("Sampler") == "—"     # not until refresh()
        s.refresh()
        assert s.section_rate_text("Sampler") == "100%"
        assert s._rate_bars["Sampler"].value() == 100
        assert s.section_rate_text("Estimator") == "—"
    finally:
        s.close(); s.deleteLater(); _pump(qapp)


def test_main_window_returning_to_setup_refreshes_rates(qapp, data_dir, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow, PAGE_SETUP, PAGE_HISTORY
    win = MainWindow()
    try:
        assert win._setup.section_rate_text("Estimator") == "—"
        persistence.save_session(_one_pass("Estimator"))
        win._on_history()
        assert win._stack.currentIndex() == PAGE_HISTORY
        win._history.back_requested.emit()
        assert win._stack.currentIndex() == PAGE_SETUP
        assert win._setup.section_rate_text("Estimator") == "100%"
    finally:
        win.close(); win.deleteLater(); _pump(qapp)

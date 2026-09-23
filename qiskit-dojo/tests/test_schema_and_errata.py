"""Schema versioning, rotating backups, and the in-app errata button.

Two features that arrived with the move onto ``common/``:

* every file this app writes carries a ``<name>.schema.json`` version sidecar,
  is rotated into ``<name>.bak`` before the first write of a session, migrates
  forward when it was written by an older build, and is **refused** rather
  than overwritten when it was written by a newer one;
* the kata screen can report a wrong kata as a prefilled GitHub issue, without
  a network call, without blocking, and without losing the report when there
  is no browser to hand it to.

All persistence goes to ``data_dir``; the browser is always stubbed.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
from PyQt6.QtCore import QObject, Qt, QUrl, pyqtSignal
from PyQt6.QtWidgets import QDialog

import persistence
from common import errata, schema
from core.models import Kata, KataAttempt, RunResult, SessionStats

APP = "qiskit-dojo"

#: (kind, file name, a write that produces it, a reader that returns its rows)
WRITTEN_FILES = ("history", "flagged", "settings", "mistakes", "confidence")


def _kata(kid: str = "ra_little_endian", title: str = "Per-qubit probabilities",
          section: str = "Results analysis") -> Kata:
    return Kata(id=kid, section=section, title=title, difficulty="beginner",
                prompt="Recover P(qubit 0 = 1) from a counts dict.",
                starter_code="x = 0\n", test_code="assert x == 1\n",
                solution_code="x = 1\n", hints=["h1"])


def _write_everything() -> None:
    """One write of every file this app owns."""
    persistence.save_session(SessionStats(
        attempts=[KataAttempt(_kata("a"), passed=True, tries=1)]))
    persistence.toggle_flag(_kata("a"))
    persistence.set_confidence_prompt_enabled(False)
    persistence.log_mistake(persistence.make_mistake_entry(
        "a", "Sampler", "q", "your", "right"))
    persistence.log_confidence("a", "Sampler", 3, False)


def _paths() -> dict[str, Path]:
    return {
        "history":    persistence.history_path(),
        "flagged":    persistence.flagged_path(),
        "settings":   persistence.settings_path(),
        "mistakes":   persistence.mistakes_path(),
        "confidence": persistence.confidence_path(),
    }


# --------------------------------------------------------------- the sidecar

def test_every_file_this_app_writes_gets_a_version_sidecar(data_dir):
    _write_everything()
    for kind, path in _paths().items():
        side = schema.sidecar_path(path)
        assert side.is_file(), f"{kind}: no sidecar beside {path.name}"
        meta = json.loads(side.read_text())
        assert meta["file"] == path.name
        assert meta["kind"] == kind
        assert meta["schema"] == schema.get(kind).version == 1
        assert meta["written_by"].startswith("common/")
        assert isinstance(meta["updated"], float)


def test_the_payload_on_disk_is_unchanged_by_versioning(data_dir):
    """The marker is a sidecar precisely so the data files keep their shape —
    coach.py and dashboard.py read plain JSON lists."""
    _write_everything()
    for name in ("dojo_history.json", "dojo_flagged.json", "mistakes.json",
                 "confidence.json"):
        assert isinstance(json.loads((data_dir / name).read_text()), list)
    assert isinstance(
        json.loads((data_dir / "dojo_settings.json").read_text()), dict)


def test_an_unmarked_file_is_read_as_v1_and_stamped_on_the_next_write(data_dir):
    """Every file written before versioning existed is a v1 file."""
    data_dir.mkdir(parents=True, exist_ok=True)
    persistence.MISTAKES_FILE.write_text(json.dumps([{
        "id": "old", "app": APP, "category": "Sampler", "question": "q",
        "your_answer": "a", "correct_answer": "b", "cause": None, "note": "",
        "timestamp": 1.0, "resolved": False}]))
    assert not schema.sidecar_path(persistence.MISTAKES_FILE).exists()
    assert schema.stored_version(persistence.MISTAKES_FILE, "mistakes") == 1
    assert [r["id"] for r in persistence.load_mistakes()] == ["old"]

    persistence.log_mistake(persistence.make_mistake_entry(
        "new", "Sampler", "q", "a", "b"))
    assert schema.read_meta(persistence.MISTAKES_FILE)["schema"] == 1
    assert [r["id"] for r in persistence.load_mistakes()] == ["old", "new"]


# ------------------------------------------------------------- migrate forward

@pytest.fixture
def history_v2():
    """Pretend this build understands a v2 history that has a "version" key."""
    def one_to_two(sessions):
        return [{**s, "app": APP} for s in sessions if isinstance(s, dict)]

    original = schema.get("history")
    schema.register(schema.FileSchema("history", version=2,
                                      migrations={1: one_to_two}), replace=True)
    try:
        yield
    finally:
        schema.register(original, replace=True)


def test_an_older_file_migrates_forward_on_read_and_is_restamped_on_write(
        data_dir, history_v2):
    data_dir.mkdir(parents=True, exist_ok=True)
    persistence.HISTORY_FILE.write_text(json.dumps(
        [{"timestamp": 1.0, "total": 1, "passed": 1, "attempts": []}]))
    assert schema.stored_version(persistence.HISTORY_FILE, "history") == 1

    sessions = persistence._load_raw()               # migrated in memory
    assert sessions[0]["app"] == APP
    # reading is never destructive: the file is still v1 until something writes
    assert schema.stored_version(persistence.HISTORY_FILE, "history") == 1
    assert "app" not in json.loads(persistence.HISTORY_FILE.read_text())[0]

    persistence.save_session(SessionStats(
        attempts=[KataAttempt(_kata("k"), passed=False, tries=2)]))
    assert schema.read_meta(persistence.HISTORY_FILE)["schema"] == 2
    on_disk = json.loads(persistence.HISTORY_FILE.read_text())
    assert [s.get("app") for s in on_disk] == [APP, None]   # old row migrated


# ------------------------------------------------------- refuse a newer file

@pytest.mark.parametrize("kind", WRITTEN_FILES)
def test_a_newer_file_is_refused_not_corrupted(data_dir, kind):
    _write_everything()
    path = _paths()[kind]
    before = path.read_text()
    schema.write_meta(path, kind, version=99)        # "written by a newer build"

    with pytest.raises(schema.SchemaTooNewError):
        schema.check_writable(path, kind)

    journal_kinds = {"mistakes", "confidence"}
    journal = pytest.importorskip("common.journal")
    journal.clear_write_error()

    if kind == "history":
        with pytest.raises(schema.SchemaTooNewError):
            persistence.save_session(SessionStats(
                attempts=[KataAttempt(_kata("z"), passed=True, tries=1)]))
    elif kind == "settings":
        with pytest.raises(schema.SchemaTooNewError):
            persistence.set_confidence_prompt_enabled(True)
    elif kind == "flagged":
        persistence.toggle_flag(_kata("z"))          # refused, never raises
    elif kind == "mistakes":
        persistence.log_mistake(persistence.make_mistake_entry(
            "z", "Sampler", "q", "a", "b"))
    else:
        persistence.log_confidence("z", "Sampler", 2, True)

    assert path.read_text() == before, f"{kind}: a newer file was overwritten"
    if kind in journal_kinds:
        # the drill must not crash; the refusal is recorded instead
        err = persistence.last_write_error()
        assert isinstance(err, schema.SchemaTooNewError)
        assert err.found == 99 and err.understood == 1
    journal.clear_write_error()


def test_reading_a_newer_file_still_works(data_dir):
    """Refusal is about writing.  A newer journal is still readable, so the
    history screen does not go blank when another machine is ahead."""
    _write_everything()
    schema.write_meta(persistence.MISTAKES_FILE, "mistakes", version=99)
    assert [r["id"] for r in persistence.load_mistakes()] == ["a"]


# ---------------------------------------------------------- rotating backups

def test_backups_rotate_one_generation_per_session(data_dir):
    path = persistence.SETTINGS_FILE
    gens = schema.backup_paths(path)

    for n, value in enumerate(("one", "two", "three", "four")):
        schema.reset_session(path)                   # "a new run of the app"
        persistence.save_settings({"marker": value})

    # the first write had nothing to back up; after four sessions three
    # generations survive, newest first
    assert [json.loads(g.read_text())["marker"] for g in gens] == [
        "three", "two", "one"]
    assert json.loads(path.read_text())["marker"] == "four"


def test_one_backup_per_session_not_per_write(data_dir):
    path = persistence.SETTINGS_FILE
    persistence.save_settings({"marker": "first"})
    schema.reset_session(path)
    for value in ("a", "b", "c"):
        persistence.save_settings({"marker": value})
    assert json.loads(schema.backup_paths(path)[0].read_text())["marker"] == "first"
    assert not schema.backup_paths(path)[1].exists()


def test_a_corrupt_file_can_be_restored_from_its_backup(data_dir):
    path = persistence.MISTAKES_FILE
    persistence.log_mistake(persistence.make_mistake_entry(
        "good", "Sampler", "q", "a", "b"))
    schema.reset_session(path)
    persistence.log_mistake(persistence.make_mistake_entry(
        "later", "Sampler", "q", "a", "b"))

    path.write_text("{ truncated mid-write")
    assert persistence.load_mistakes() == []         # corrupt reads as empty
    assert schema.restore_backup(path) is True
    assert [r["id"] for r in persistence.load_mistakes()] == ["good"]


# ---------------------------------------------------------------- the errata
#                                                                    control

class _FakeWorker(QObject):
    finished_run = pyqtSignal(object)
    failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, user_code: str, test_code: str, parent=None) -> None:
        super().__init__(parent)

    def start(self) -> None:
        pass


def _pump(qapp, n: int = 3) -> None:
    for _ in range(n):
        qapp.processEvents()


class _Browser(list):
    """Records every URL handed to QDesktopServices; ``ok`` makes it fail."""
    ok = True


@pytest.fixture
def opened(monkeypatch):
    """Stub QDesktopServices everywhere the report path can reach it."""
    urls = _Browser()
    import common.ui.errata_dialog as ed
    import ui.screens.kata_screen as ks

    def fake_open(url):
        urls.append(url.toString())
        return urls.ok

    monkeypatch.setattr(ed.QDesktopServices, "openUrl", staticmethod(fake_open))
    monkeypatch.setattr(ks.QDesktopServices, "openUrl", staticmethod(fake_open))
    return urls


@pytest.fixture
def screen(qapp, data_dir, monkeypatch):
    import ui.screens.kata_screen as mod
    monkeypatch.setattr(mod, "RunWorker", _FakeWorker)
    s = mod.KataScreen()
    yield s
    s.close(); s.deleteLater(); _pump(qapp)


def _fill_dialog(dialog, why: str, fix: str = "", severity: str = "") -> None:
    dialog._why.setPlainText(why)
    if fix:
        dialog._fix.setPlainText(fix)
    if severity:
        dialog._severity.setCurrentIndex(
            dialog._severity.findData(severity))


def test_the_report_button_is_present_focusable_and_named(screen):
    btn = screen._errata_btn
    assert btn.text() == "⚠ Report a problem"
    assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert btn.accessibleName() and btn.accessibleDescription()
    assert btn.toolTip() == btn.accessibleDescription()
    # it lives in the kata screen's button row, next to Flag for review
    row = screen._flag_btn.parent()
    assert btn.parent() is row


def test_the_button_tracks_the_kata_on_screen(screen, qapp, opened, monkeypatch):
    import common.ui.errata_dialog as ed
    seen: list[tuple[str, str]] = []

    class _Accept(ed.ErrataDialog):
        def exec(self):                              # noqa: D102 - test double
            seen.append((self._item_id, self._item_text))
            _fill_dialog(self, "the test asserts the wrong bit order")
            self._on_accept()
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr(ed, "ErrataDialog", _Accept)

    k = _kata("ra_little_endian", title="Per-qubit probabilities")
    screen.show_kata(k, 1, 1)
    url = screen._errata_btn.report()
    assert seen == [("ra_little_endian", f"{k.title}\n\n{k.prompt}")]

    screen.show_kata(_kata("sam_basic", title="Sampler basics",
                           section="Sampler"), 1, 1)
    screen._errata_btn.report()
    assert seen[1][0] == "sam_basic"
    # QUrl.toString() is the browser's pretty form of the same link
    assert url and QUrl(url).toString() in opened


def test_the_url_is_a_prefilled_content_error_form(screen, qapp, opened,
                                                   monkeypatch):
    import common.ui.errata_dialog as ed

    class _Accept(ed.ErrataDialog):
        def exec(self):                              # noqa: D102 - test double
            _fill_dialog(self, "Sampler v2 has no .result().get_counts()",
                         fix="use result()[0].data.meas.get_counts()",
                         severity="wrong")
            self._on_accept()
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr(ed, "ErrataDialog", _Accept)
    screen.show_kata(_kata("sam_basic", title="Sampler basics",
                           section="Sampler"), 1, 1)

    url = screen._errata_btn.report()
    assert url and opened == [QUrl(url).toString()]
    parsed = urlparse(url)
    assert parsed.netloc == "github.com"
    assert parsed.path == f"/{errata.REPO}/issues/new"
    q = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    assert q["template"] == "content_error.yml"
    assert q["title"] == "[content] qiskit-dojo: sam_basic"
    assert "qiskit-dojo/katas/" in q["file"] and "sam_basic" in q["file"]
    assert "Sampler basics" in q["quote"]
    assert "no .result().get_counts()" in q["why_wrong"]
    assert "data.meas.get_counts()" in q["correction"]
    assert q["severity"] == errata.SEVERITIES["wrong"]
    assert len(url) <= errata.MAX_URL
    # the form the URL names is really in this repository
    repo_root = Path(__file__).resolve().parents[2]
    assert (repo_root / ".github" / "ISSUE_TEMPLATE" / q["template"]).is_file()


def test_cancelling_reports_nothing_and_opens_nothing(screen, qapp, opened,
                                                      monkeypatch):
    import common.ui.errata_dialog as ed
    fired: list[str] = []
    screen._errata_btn.reported.connect(fired.append)

    class _Cancel(ed.ErrataDialog):
        def exec(self):                              # noqa: D102 - test double
            return QDialog.DialogCode.Rejected

    monkeypatch.setattr(ed, "ErrataDialog", _Cancel)
    screen.show_kata(_kata(), 1, 1)
    assert screen._errata_btn.report() is None
    assert opened == [] and fired == []


def test_no_browser_shows_the_url_instead_of_swallowing_the_report(
        screen, qapp, opened, monkeypatch):
    """A machine with no browser must not lose the report."""
    import common.ui.errata_dialog as ed
    import ui.screens.kata_screen as ks
    opened.ok = False                                # openUrl fails
    shown: list[tuple[str, str]] = []

    class _Accept(ed.ErrataDialog):
        def exec(self):                              # noqa: D102 - test double
            _fill_dialog(self, "wrong expected value")
            self._on_accept()
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr(ed, "ErrataDialog", _Accept)
    monkeypatch.setattr(ks.QMessageBox, "exec",
                        lambda self: shown.append((self.text(),
                                                   self.informativeText())))

    screen.show_kata(_kata(), 1, 1)
    url = screen._errata_btn.report()
    assert url
    assert len(shown) == 1
    assert "No browser" in shown[0][0]
    assert shown[0][1] == url                        # the whole link, copyable


def test_reporting_writes_nothing_and_needs_no_network(screen, qapp, opened,
                                                       data_dir, monkeypatch):
    import common.ui.errata_dialog as ed

    class _Accept(ed.ErrataDialog):
        def exec(self):                              # noqa: D102 - test double
            _fill_dialog(self, "typo in the prompt")
            self._on_accept()
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr(ed, "ErrataDialog", _Accept)
    screen.show_kata(_kata(), 1, 1)
    screen._errata_btn.report()
    assert not data_dir.exists()                     # errata is not persistence
    assert len(opened) == 1


def test_the_dialog_will_not_submit_an_empty_report(screen, qapp):
    from common.ui.errata_dialog import ErrataDialog
    screen.show_kata(_kata(), 1, 1)
    dialog = ErrataDialog(screen, app=APP, item_id="ra_little_endian",
                          item_text="Per-qubit probabilities")
    try:
        assert not dialog._open_btn.isEnabled()
        dialog._why.setPlainText("   ")
        _pump(qapp)
        assert not dialog._open_btn.isEnabled()
        dialog._why.setPlainText("the counts are little-endian, not big")
        _pump(qapp)
        assert dialog._open_btn.isEnabled()
        assert dialog.issue_url is None              # nothing built until accept
        assert "little-endian" in dialog.build_url()
    finally:
        dialog.close(); dialog.deleteLater(); _pump(qapp)


def test_the_run_loop_is_unaffected_by_the_new_button(screen, qapp, data_dir):
    """The report control is inert until it is pressed: the pass/fail flow,
    the journal and the flag list all behave exactly as before."""
    k = _kata()
    screen.show_kata(k, 1, 1)
    screen._run_btn.click(); _pump(qapp)
    screen._run_worker.finished_run.emit(
        RunResult(passed=False, output="FAILED: nope", phase="test_failed",
                  duration_secs=0.1))
    screen._run_worker.finished.emit(); _pump(qapp)
    assert screen._status_lbl.text().startswith("✗ TESTS FAILED")
    assert len(persistence.load_mistakes()) == 1

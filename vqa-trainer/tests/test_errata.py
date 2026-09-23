""""Report a problem with this item" — headless drive of the whole path.

The repository is public.  When a problem's answer key is wrong or its wording
is ambiguous there was no route from "this is wrong" to a fix except
remembering it later, and nobody remembers it later.  The control on the
result screen is that route: one click, three fields, and a GitHub issue that
is already filled in with the problem id and the text as the learner saw it.

What these tests pin:

* the button is on the result screen, keyboard reachable and named for a
  screen reader, and points at the problem currently shown;
* the dialog will not build a report with no description;
* the URL it builds carries this app's id, the problem's id, the problem text
  *including its choices*, and lands in the issue form's own fields;
* the browser call is the last step, it is never made until the learner
  confirms, and when there is no browser the link goes to the clipboard and a
  message is shown instead of the report being lost;
* nothing here blocks or breaks the session.
"""
from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import errata
from common.ui.errata_dialog import ErrataDialog
from core.models import Attempt, GradeMode, Problem, Verdict
from ui.screens.result_screen import ResultScreen, item_text

PAGE_PROBLEM, PAGE_RESULT = 1, 2


def _problem(pid: str = "qaoa_mixer_role") -> Problem:
    return Problem(
        id=pid, category="QAOA", difficulty="beginner",
        question="Which operator does QAOA apply first in each layer?",
        choices=["The cost operator U_C", "The mixer U_B", "A Hadamard", "A measurement"],
        correct_index=0, explanation="U_C then U_B.", grade_mode=GradeMode.MC,
    )


def _attempt(problem: Problem | None = None) -> Attempt:
    p = problem or _problem()
    return Attempt(p, "B", 0, Verdict.INCORRECT, "Not quite.")


@pytest.fixture
def screen(qapp):
    s = ResultScreen()
    s.show_attempt(_attempt(), is_last=False)
    s.show()
    qapp.processEvents()
    try:
        yield s
    finally:
        s.close()


# ── the control ──────────────────────────────────────────────────────────────

def test_the_button_is_on_the_result_screen_and_keyboard_reachable(screen):
    btn = screen._errata_btn
    assert btn.isVisibleTo(screen)
    assert btn.isEnabled()
    assert "Report a problem" in btn.text()
    assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert btn.accessibleName() and btn.accessibleDescription()
    assert btn.toolTip()
    btn.setFocus()
    assert btn.hasFocus(), "the control must be reachable without a mouse"


def test_the_button_is_disabled_until_a_problem_is_on_screen(qapp):
    fresh = ResultScreen()
    try:
        assert not fresh._errata_btn.isEnabled()
        fresh.show_attempt(_attempt(), is_last=False)
        assert fresh._errata_btn.isEnabled()
    finally:
        fresh.close()


def test_the_button_follows_whichever_problem_is_shown(screen):
    screen.show_attempt(_attempt(_problem("bp_definition")), is_last=True)
    url = screen._errata_btn._item_id
    assert url == "bp_definition"
    fields = parse_qs(urlparse(
        errata.issue_url("vqa-trainer", screen._errata_btn._item_id,
                         screen._errata_btn._item_text, "x")).query)
    assert "bp_definition" in fields["title"][0]


# ── what the report says ─────────────────────────────────────────────────────

def test_the_quoted_text_includes_the_choices_the_learner_saw(screen):
    text = item_text(_attempt())
    assert text.startswith("Which operator does QAOA apply first in each layer?")
    assert "A. The cost operator U_C" in text
    assert "D. A measurement" in text
    assert screen._errata_btn._item_text == text


def test_a_numeric_problem_quotes_its_expected_value():
    numeric = Problem(id="ps_numeric_sin", category="Parameter Shift",
                      difficulty="advanced", question="Evaluate the shift.",
                      correct_value=-0.8660254, grade_mode=GradeMode.AUTO)
    text = item_text(Attempt(numeric, "0.5", 0, Verdict.INCORRECT, "fb"))
    assert "Evaluate the shift." in text and "-0.866025" in text


def test_the_dialog_builds_a_url_into_the_issue_forms_own_fields(qapp):
    dialog = ErrataDialog(app="vqa-trainer", item_id="qaoa_mixer_role",
                          item_text=item_text(_attempt()))
    try:
        assert not dialog._open_btn.isEnabled(), "no description, no report"
        dialog._why.setPlainText("The key says A but the mixer is applied first.")
        assert dialog._open_btn.isEnabled()
        dialog._fix.setPlainText("The correct choice is B.")
        dialog._severity.setCurrentIndex(
            list(errata.SEVERITIES).index("misleading"))

        url = dialog.build_url()
        parsed = urlparse(url)
        assert parsed.netloc == "github.com"
        assert parsed.path.endswith("/issues/new")
        q = parse_qs(parsed.query)
        assert q["template"] == ["content_error.yml"]
        assert q["title"] == ["[content] vqa-trainer: qaoa_mixer_role"]
        assert q["file"] == ["vqa-trainer/problems/ — item id `qaoa_mixer_role`"]
        assert "The mixer U_B" in q["quote"][0]
        assert q["why_wrong"] == ["The key says A but the mixer is applied first."]
        assert q["correction"] == ["The correct choice is B."]
        assert q["severity"] == [errata.SEVERITIES["misleading"]]
        assert len(url) <= errata.MAX_URL
    finally:
        dialog.close()


# ── opening it (the browser call is always stubbed) ──────────────────────────

def _accept_with(monkeypatch, comment: str):
    """Make the next ErrataDialog fill itself in and accept, with no modal."""
    import common.ui.errata_dialog as mod

    real = mod.ErrataDialog

    class AutoDialog(real):                      # type: ignore[misc,valid-type]
        def exec(self) -> int:
            self._why.setPlainText(comment)
            self._on_accept()
            return QDialog.DialogCode.Accepted.value

    monkeypatch.setattr(mod, "ErrataDialog", AutoDialog)


def test_clicking_through_opens_the_prefilled_issue_in_the_browser(
        screen, monkeypatch):
    opened: list[str] = []
    import ui.screens.result_screen as rs

    monkeypatch.setattr(rs.QDesktopServices, "openUrl",
                        staticmethod(lambda url: opened.append(url.toString()) or True))
    _accept_with(monkeypatch, "The answer key is wrong.")

    seen: list[str] = []
    screen.errata_reported.connect(seen.append)
    screen._errata_btn.click()

    assert len(opened) == 1 and len(seen) == 1
    assert opened[0].startswith("https://github.com/")
    # The signal carries the URL as built; QUrl.toString() normalises some of
    # the escaping, so the fields are checked on the unmodified string.
    q = parse_qs(urlparse(seen[0]).query)
    assert q["why_wrong"] == ["The answer key is wrong."]
    assert "qaoa_mixer_role" in q["title"][0]
    assert screen.errata_note() == "", "no fallback message when it worked"


def test_cancelling_the_dialog_opens_nothing(screen, monkeypatch):
    opened: list[str] = []
    import common.ui.errata_dialog as mod
    import ui.screens.result_screen as rs

    monkeypatch.setattr(rs.QDesktopServices, "openUrl",
                        staticmethod(lambda url: opened.append(url.toString()) or True))
    monkeypatch.setattr(mod.ErrataDialog, "exec",
                        lambda self: QDialog.DialogCode.Rejected.value)

    seen: list[str] = []
    screen.errata_reported.connect(seen.append)
    assert screen._errata_btn.report() is None
    assert opened == [] and seen == []


def test_no_browser_degrades_to_the_clipboard_and_a_visible_message(
        screen, qapp, monkeypatch):
    import ui.screens.result_screen as rs

    monkeypatch.setattr(rs.QDesktopServices, "openUrl",
                        staticmethod(lambda url: False))
    _accept_with(monkeypatch, "Ambiguous wording.")

    seen: list[str] = []
    screen.errata_reported.connect(seen.append)
    screen._errata_btn.click()

    assert len(seen) == 1, "the report is still reported"
    assert "clipboard" in screen.errata_note()
    assert screen._errata_note.toolTip() == seen[0]
    clipboard = qapp.clipboard()
    assert clipboard is not None and clipboard.text() == seen[0]

    # …and it clears the moment the next problem is shown.
    screen.show_attempt(_attempt(_problem("bp_definition")), is_last=False)
    assert screen.errata_note() == ""


def test_a_browser_that_throws_never_reaches_the_session(screen, monkeypatch):
    import ui.screens.result_screen as rs

    def boom(_url):
        raise RuntimeError("no D-Bus portal here")

    monkeypatch.setattr(rs.QDesktopServices, "openUrl", staticmethod(boom))
    _accept_with(monkeypatch, "Wrong.")

    screen._errata_btn.click()                   # must not raise
    assert "clipboard" in screen.errata_note()


def test_reporting_does_not_disturb_the_rest_of_the_result_screen(
        screen, monkeypatch):
    import ui.screens.result_screen as rs

    monkeypatch.setattr(rs.QDesktopServices, "openUrl", staticmethod(lambda url: True))
    _accept_with(monkeypatch, "Wrong.")

    screen._mistake_row._note.setText("keep me")
    screen._errata_btn.click()
    assert screen._mistake_row.note() == "keep me"
    assert screen.journal_visible(), "the journal row is still there"

    advanced: list[int] = []
    screen.next_requested.connect(lambda: advanced.append(1))
    screen._next_btn.click()
    assert advanced == [1]


# ── in the running window ────────────────────────────────────────────────────

def test_the_control_is_reachable_from_a_real_session(qapp, monkeypatch,
                                                      isolated_data_dir):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import ui.main_window as mw
    import ui.screens.result_screen as rs

    monkeypatch.setattr(mw, "build_problem_set", lambda cfg: [_problem()])
    opened: list[str] = []
    monkeypatch.setattr(rs.QDesktopServices, "openUrl",
                        staticmethod(lambda url: opened.append(url.toString()) or True))
    _accept_with(monkeypatch, "This problem's key is wrong.")

    win = mw.MainWindow()
    try:
        win._setup._start_btn.click()
        assert win._stack.currentIndex() == PAGE_PROBLEM
        win._problem._radio_btns[1].setChecked(True)
        win._problem._validate_mc()
        win._problem._submit_btn.click()
        assert win._stack.currentIndex() == PAGE_RESULT

        reported: list[str] = []
        win._result.errata_reported.connect(reported.append)
        win._result._errata_btn.click()
        assert len(opened) == 1 and len(reported) == 1
        q = parse_qs(urlparse(reported[0]).query)
        assert q["file"] == ["vqa-trainer/problems/ — item id `qaoa_mixer_role`"]
        assert q["why_wrong"] == ["This problem's key is wrong."]
    finally:
        win.close()

"""In-app errata reporting: "⚑ Report a problem with this item".

The repository is public, so a wrong rubric, a sign error in a model solution
or an ambiguous derivation step needs a path from "this is wrong" to a fix.
The control sits where the item is on screen — the problem part's button row,
beside "Show model solution", and the derivation step card — collects the
defect in the shared :class:`common.ui.errata_dialog.ErrataDialog`, and hands
``QDesktopServices`` a **prefilled GitHub issue URL** built by
:mod:`common.errata`.

What these tests pin:

* the control is present, keyboard reachable and named, on both screens, and
  follows the item on screen;
* it **never blocks**: the form is modeless, the click returns immediately, and
  the drill behind it keeps working while it is open;
* the URL is prefilled with this app's item path, the item id, the text the
  learner saw and what they typed, against the repository's content-error form;
* nothing is opened when the form is cancelled;
* with no browser (``openUrl`` returns False) the report is **not lost** — the
  URL is offered for copying instead;
* it is pure: no network, no writes.
"""
from __future__ import annotations

from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import pytest
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QDialog

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import errata
from common.ui import errata_dialog as shared_dialog
from ui.widgets import errata as app_errata
from ui.widgets.errata import REPORT_TEXT, ErrataButton, quote_for

APP = "problem-trainer"


@pytest.fixture
def browser(monkeypatch):
    """Stub QDesktopServices; ``opened`` records every URL handed to it."""
    opened: list[QUrl] = []
    state = SimpleNamespace(opened=opened, ok=True)
    monkeypatch.setattr(app_errata, "QDesktopServices", SimpleNamespace(
        openUrl=lambda url: (opened.append(url), state.ok)[1]))
    return state


def _submit(btn, why: str, correction: str = "", severity: str | None = None):
    """Fill in the open form the way a user would and press the accept button."""
    dialog = btn.dialog
    assert dialog is not None, "the report form is not open"
    dialog._why.setPlainText(why)
    if correction:
        dialog._fix.setPlainText(correction)
    if severity is not None:
        dialog._severity.setCurrentIndex(dialog._severity.findData(severity))
    assert dialog._open_btn.isEnabled()
    dialog._open_btn.click()


def _query(url: str) -> dict[str, str]:
    return {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}


def _reported(btn) -> list[str]:
    seen: list[str] = []
    btn.reported.connect(seen.append)
    return seen


# ---------------------------------------------------------------------------
# The control, where the item is
# ---------------------------------------------------------------------------

def test_the_problem_part_offers_the_control_beside_the_model_solution(
        main_window, data_dir, problems, qapp):
    from ui.screens.problem_screen import part_item_id
    from ui.screens.setup_screen import MODE_PROBLEMS

    win = main_window
    problem = problems[0]
    win._setup.session_started.emit(MODE_PROBLEMS, [problem])
    qapp.processEvents()

    for part in problem.parts:
        widget = win._problem._part_widgets[part.part_id]
        btn = widget._errata_btn
        assert btn.text() == REPORT_TEXT
        assert btn.isVisibleTo(widget), "available whenever the item is on screen"
        assert btn._item_id == part_item_id(problem, part)
        assert part.prompt.strip()[:40] in btn._item_text
        assert part.model_solution.strip()[:40] in btn._item_text


def test_the_derivation_step_card_offers_the_control_and_follows_the_step(
        main_window, data_dir, derivations, qapp):
    from ui.screens.derivation_screen import step_item_id
    from ui.screens.setup_screen import MODE_DERIVATIONS

    win = main_window
    deriv = next(d for d in derivations if len(d.steps) >= 2)
    win._setup.session_started.emit(MODE_DERIVATIONS, [deriv])
    qapp.processEvents()
    screen = win._derivation
    btn = screen._errata_btn

    assert btn._item_id == step_item_id(deriv, deriv.steps[0])
    assert deriv.steps[0].prompt.strip()[:40] in btn._item_text

    screen._answer_edit.setPlainText("skip ahead")
    screen._reveal_btn.click()                      # advance to step 2
    qapp.processEvents()
    assert btn._item_id == step_item_id(deriv, deriv.steps[1])
    assert deriv.steps[1].prompt.strip()[:40] in btn._item_text


def test_the_control_is_keyboard_reachable_and_named(qapp):
    btn = ErrataButton(item_id="x:a", item_text="q")
    try:
        assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
        assert btn.accessibleName()
        assert btn.toolTip()
        assert ":focus" in btn.styleSheet()          # a visible focus ring
    finally:
        btn.deleteLater()
        qapp.processEvents()


# ---------------------------------------------------------------------------
# It never blocks
# ---------------------------------------------------------------------------

def test_the_form_is_modeless_and_the_click_returns_immediately(qapp, browser):
    btn = ErrataButton(item_id="x:a", item_text="q")
    try:
        assert btn.dialog is None
        btn.click()                       # would not return until closed if exec()
        qapp.processEvents()
        assert btn.dialog is not None
        assert not btn.dialog.isModal()
        assert btn.dialog.isVisible()
        btn.click()                       # a second click raises, never stacks
        qapp.processEvents()
        assert btn.dialog is not None
        btn.dialog.reject()
        qapp.processEvents()
        assert btn.dialog is None
    finally:
        btn.deleteLater()
        qapp.processEvents()


def test_the_drill_keeps_working_while_a_report_is_open(
        main_window, data_dir, problems, qapp, browser, find_button):
    """A half-written report must not freeze the problem behind it."""
    from ui.screens.setup_screen import MODE_PROBLEMS

    win = main_window
    problem = problems[0]
    win._setup.session_started.emit(MODE_PROBLEMS, [problem])
    qapp.processEvents()
    widget = win._problem._part_widgets[problem.parts[0].part_id]

    widget._errata_btn.click()
    qapp.processEvents()
    assert widget._errata_btn.dialog is not None

    widget._answer_edit.setPlainText("still typing my answer")
    qapp.processEvents()
    assert widget._submit_btn.isEnabled(), "the drill is still live"
    find_button(widget, "Show model solution").click()
    qapp.processEvents()
    assert widget.state.solution_revealed

    _submit(widget._errata_btn, "the rubric contradicts the model solution")
    qapp.processEvents()
    assert widget._errata_btn.dialog is None
    assert len(browser.opened) == 1
    assert widget._answer_edit.toPlainText() == "still typing my answer"


# ---------------------------------------------------------------------------
# What it opens
# ---------------------------------------------------------------------------

def test_reporting_opens_a_prefilled_issue_for_this_item(qapp, browser):
    btn = ErrataButton(item_id="la_schmidt:a",
                       item_text=quote_for("Part (a)", "Compute the Schmidt rank.",
                                           "Model solution", "rank 2"))
    seen = _reported(btn)
    try:
        btn.click()
        qapp.processEvents()
        _submit(btn, "The model solution has the sign of the phase backwards.",
                correction="e^{-iθ}, not e^{+iθ}", severity="wrong")
        qapp.processEvents()

        assert len(seen) == 1
        url = seen[0]
        assert browser.opened == [QUrl(url)]

        parsed = urlparse(url)
        assert parsed.scheme == "https" and parsed.netloc == "github.com"
        assert parsed.path == f"/{errata.REPO}/issues/new"
        q = _query(url)
        assert q["template"] == "content_error.yml"
        assert q["title"] == "[content] problem-trainer: la_schmidt:a"
        assert "problem-trainer/problems/" in q["file"]
        assert "la_schmidt:a" in q["file"]
        assert "Compute the Schmidt rank." in q["quote"]
        assert "rank 2" in q["quote"]
        assert "sign of the phase backwards" in q["why_wrong"]
        assert q["correction"] == "e^{-iθ}, not e^{+iθ}"
        assert q["severity"] == errata.SEVERITIES["wrong"]
    finally:
        btn.deleteLater()
        qapp.processEvents()


def test_cancelling_reports_nothing_and_opens_nothing(qapp, browser):
    btn = ErrataButton(item_id="x:a", item_text="q")
    seen = _reported(btn)
    try:
        btn.click()
        qapp.processEvents()
        btn.dialog._why.setPlainText("typed but then cancelled")
        btn.dialog.reject()
        qapp.processEvents()
        assert seen == [] and browser.opened == []
    finally:
        btn.deleteLater()
        qapp.processEvents()


def test_the_form_will_not_submit_an_empty_report(qapp):
    dialog = shared_dialog.ErrataDialog(None, app=APP, item_id="x:a", item_text="q")
    try:
        assert not dialog._open_btn.isEnabled()
        dialog._why.setPlainText("   ")
        assert not dialog._open_btn.isEnabled()
        dialog._why.setPlainText("this is wrong")
        assert dialog._open_btn.isEnabled()
    finally:
        dialog.deleteLater()


def test_a_very_long_item_still_produces_a_usable_url(qapp, browser):
    btn = ErrataButton(item_id="deriv_qpe:s1", item_text="ψ" * 20000)
    seen = _reported(btn)
    try:
        btn.click()
        qapp.processEvents()
        _submit(btn, "wrong")
        qapp.processEvents()
        url = seen[0]
        assert len(url) <= errata.MAX_URL
        q = _query(url)
        assert q["title"] == "[content] problem-trainer: deriv_qpe:s1"
        assert "deriv_qpe:s1" in q["file"]           # the short fields survive
    finally:
        btn.deleteLater()
        qapp.processEvents()


# ---------------------------------------------------------------------------
# Degrading with no browser
# ---------------------------------------------------------------------------

def test_with_no_browser_the_url_is_offered_for_copying_instead(
        qapp, browser, monkeypatch):
    browser.ok = False                        # openUrl fails, as on a bare tty
    shown: list[str] = []
    monkeypatch.setattr(ErrataButton, "show_url_fallback",
                        lambda self, url: shown.append(url))

    btn = ErrataButton(item_id="x:a", item_text="q")
    seen = _reported(btn)
    try:
        btn.click()
        qapp.processEvents()
        _submit(btn, "wrong")                 # must not raise
        qapp.processEvents()
        assert len(seen) == 1
        assert browser.opened == [QUrl(seen[0])], "it did try the browser first"
        assert shown == [seen[0]], "and the report was not lost"
    finally:
        btn.deleteLater()
        qapp.processEvents()


def test_the_fallback_dialog_shows_the_whole_url_selectable(qapp):
    btn = ErrataButton(item_id="x:a", item_text="q")
    try:
        url = errata.issue_url(APP, "x:a", "q", "wrong")
        dialog = btn.fallback_dialog(url)
        assert dialog.url_box.toPlainText() == url
        assert dialog.url_box.isReadOnly()
        assert dialog.url_box.accessibleName()
        dialog.deleteLater()
    finally:
        btn.deleteLater()
        qapp.processEvents()


def test_the_fallback_is_modeless_too(qapp):
    btn = ErrataButton(item_id="x:a", item_text="q")
    try:
        btn.show_url_fallback("https://example.org/x")
        qapp.processEvents()
        assert btn._fallback is not None and not btn._fallback.isModal()
        btn._fallback.reject()
        qapp.processEvents()
        assert btn._fallback is None
    finally:
        btn.deleteLater()
        qapp.processEvents()


def test_a_desktop_that_raises_is_treated_as_no_browser(qapp, monkeypatch):
    def boom(_url):
        raise RuntimeError("no platform integration")

    monkeypatch.setattr(app_errata, "QDesktopServices",
                        SimpleNamespace(openUrl=boom))
    assert ErrataButton.open_in_browser("https://example.org") is False


# ---------------------------------------------------------------------------
# Purity
# ---------------------------------------------------------------------------

def test_reporting_writes_nothing_to_the_data_directory(qapp, browser, data_dir):
    before = sorted(p.name for p in data_dir.iterdir()) if data_dir.exists() else []
    btn = ErrataButton(item_id="p:a", item_text="prompt")
    try:
        btn.click()
        qapp.processEvents()
        _submit(btn, "wrong")
        qapp.processEvents()
        after = sorted(p.name for p in data_dir.iterdir()) if data_dir.exists() else []
        assert before == after
    finally:
        btn.deleteLater()
        qapp.processEvents()


def test_quote_for_labels_the_parts_and_drops_the_empty_ones():
    text = quote_for("Problem", "Schmidt rank", "Part (a)", "  ", "Model solution", "2")
    assert "Problem:\nSchmidt rank" in text
    assert "Model solution:\n2" in text
    assert "Part (a)" not in text
    assert quote_for() == ""

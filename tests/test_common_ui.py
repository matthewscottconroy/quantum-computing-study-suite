"""``common.ui.theme``, ``common.ui.widgets`` and ``common.ui.errata_dialog``.

Offscreen Qt.  The theme tests are the interesting ones: they check the shared
palette against the ten app copies it was extracted from, so a well-meant
"tidy-up" of a colour cannot silently restyle the whole suite.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from common import errata                           # noqa: E402
from common.ui import theme, widgets                # noqa: E402

APPS = sorted(p.parent.name for p in ROOT.glob("*/main.py"))


@pytest.fixture(scope="module")
def qapp():
    from PyQt6.QtWidgets import QApplication
    yield QApplication.instance() or QApplication([])


@pytest.fixture
def host(qapp):
    from PyQt6.QtWidgets import QWidget
    w = QWidget()
    w.resize(600, 400)
    yield w
    w.deleteLater()


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

PALETTE = ("BG", "SURFACE", "SURFACE2", "BORDER", "ACCENT", "ACCENT2", "TEXT",
           "TEXT_MUTED", "SUCCESS", "WARNING", "ERROR", "PARTIAL")


def test_no_app_redefines_a_shared_palette_constant():
    """The twelve palette constants were byte-identical in all ten ui/theme.py
    copies; the migration onto ``common.ui.theme`` removed them from the apps.
    Re-declaring one locally is how duplication creeps back, so it is an error:
    an app that wants a different colour must give it its own name."""
    pattern = re.compile(r"^([A-Z][A-Z0-9_]*)\s*=\s*\"(#[0-9a-fA-F]{6})\"", re.M)
    offenders, checked = [], 0
    for app in APPS:
        theme_py = ROOT / app / "ui" / "theme.py"
        if not theme_py.is_file():
            continue
        checked += 1
        src = theme_py.read_text(encoding="utf-8")
        for name, value in pattern.findall(src):
            if name in PALETTE:
                offenders.append(f"{app}/ui/theme.py redefines {name} = {value}")
        assert "common.ui" in src or "common import" in src, (
            f"{app}/ui/theme.py no longer redefines the palette but does not "
            f"import the shared one either")
    assert not offenders, offenders
    assert checked == len(APPS), "not every app theme was inspected"


def test_exam_sims_flag_is_partial_under_another_name():
    """exam-sim called PARTIAL "FLAG"; the shared theme keeps the alias so the
    migration did not have to rename it at every call site."""
    assert theme.FLAG == theme.PARTIAL == "#e3b341"


@pytest.mark.parametrize("percent,suffix", [(0, "00"), (13, "21"), (33, "54"),
                                            (100, "ff"), (-5, "00"), (200, "ff")])
def test_alpha_builds_an_eight_digit_colour(percent, suffix):
    assert theme.alpha("#58a6ff", percent) == f"#58a6ff{suffix}"


def test_the_base_stylesheet_carries_the_accessibility_rules():
    """Focus-visible existed in two of ten copies; it is not optional."""
    for rule in ("QPushButton:focus", "QPushButton#accent:focus",
                 "QPushButton#flat:focus", "QRadioButton:focus",
                 "QCheckBox:focus"):
        assert rule in theme.QSS, f"missing focus rule: {rule}"
    # The focused padding compensates for the wider border, so tabbing never
    # shifts the layout.
    assert "border: 2px solid" in theme.QSS and "padding: 7px 17px" in theme.QSS


def test_the_base_stylesheet_carries_the_pill_rules():
    for rule in ("QPushButton#pill", "QPushButton#pill:checked",
                 "QPushButton#pill:focus"):
        assert rule in theme.QSS


def test_the_stylesheet_is_fully_substituted_and_balanced():
    """A doubled brace typo in the f-string leaves a literal ``{ACCENT}`` in
    the sheet, which Qt drops silently along with the rest of the rule."""
    leftovers = re.findall(r"\{[A-Za-z_][A-Za-z0-9_]*\}", theme.QSS)
    assert not leftovers, f"unsubstituted placeholders: {sorted(set(leftovers))}"
    assert theme.QSS.count("{") == theme.QSS.count("}")
    for name in PALETTE:
        assert getattr(theme, name) in theme.QSS or name in ("SUCCESS",
                                                             "WARNING",
                                                             "ERROR",
                                                             "PARTIAL")


def test_extend_appends_app_rules():
    extra = "QLabel#myThing { color: red; }"
    out = theme.extend(extra)
    assert out.startswith(theme.QSS) and extra in out
    assert theme.extend() == theme.QSS


def test_apply_sets_the_stylesheet_and_font(qapp):
    previous = qapp.styleSheet()
    try:
        theme.apply(qapp)
        assert qapp.styleSheet() == theme.QSS
        theme.apply(qapp, theme.extend("QLabel#x { color: red; }"))
        assert "QLabel#x" in qapp.styleSheet()
        assert qapp.font().family()
    finally:
        qapp.setStyleSheet(previous)


def test_the_mono_stack_is_available_both_ways():
    assert isinstance(theme.MONO_FAMILIES, list)
    assert theme.MONO == theme.MONO_FAMILY
    assert "JetBrains Mono" in theme.MONO and '"' in theme.MONO


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------

def test_loading_overlay_shows_hides_and_stops_its_timer(host):
    overlay = widgets.LoadingOverlay(host)
    assert overlay.isHidden()
    overlay.show_message("Grading", "this may take a moment")
    assert overlay.size() == host.size()
    assert overlay._sub.text() == "this may take a moment"
    assert overlay._timer.isActive()
    overlay._tick()
    assert overlay._label.text() == "Grading."
    overlay._tick()
    assert overlay._label.text() == "Grading.."
    overlay.hide_overlay()
    assert overlay.isHidden()
    assert not overlay._timer.isActive(), (
        "five of the ten copies had no hide_overlay() and left the timer running")


def test_loading_overlay_keeps_the_old_method_name(host):
    overlay = widgets.LoadingOverlay(host)
    assert widgets.LoadingOverlay.show_with_message is \
        widgets.LoadingOverlay.show_message
    overlay.show_with_message("Working")
    assert not overlay.isHidden()
    overlay.hide_overlay()


def test_loading_overlay_survives_a_non_widget_parent(qapp):
    """The plain family resized against ``self.parent()``, which may not be a
    widget at all; ``parentWidget()`` is the correct accessor."""
    overlay = widgets.LoadingOverlay(None)          # type: ignore[arg-type]
    overlay.show_message("Working")                 # must not raise
    overlay.hide_overlay()
    overlay.deleteLater()


def test_collapsible_panel_toggles(host):
    from PyQt6.QtWidgets import QLabel
    content = QLabel("a long model answer")
    panel = widgets.CollapsiblePanel("Model answer", content, host)
    assert panel.expanded is False
    assert panel._toggle.text().startswith("▶")
    panel.set_expanded(True)
    assert panel.expanded is True
    assert panel._toggle.text().startswith("▼")
    assert "Model answer" in panel._toggle.text()
    panel.set_expanded(False)
    assert panel.expanded is False


def test_collapsible_panel_can_start_open(host):
    from PyQt6.QtWidgets import QLabel
    panel = widgets.CollapsiblePanel("Hints", QLabel("h"), host, expanded=True)
    assert panel.expanded is True


def test_collapsible_panel_wraps_content_in_a_scroll_area(host):
    """quantum-quiz's improvement: a long model answer scrolls inside the
    panel instead of pushing the screen off the bottom."""
    from PyQt6.QtWidgets import QLabel, QScrollArea
    panel = widgets.CollapsiblePanel("A", QLabel("x" * 5000), host)
    assert isinstance(panel._area, QScrollArea)
    assert panel._area.widgetResizable()


def test_pill_badge(host):
    pill = widgets.PillBadge("Algorithms", theme.ACCENT, host)
    assert pill.text() == "Algorithms"
    assert theme.alpha(theme.ACCENT, 13) in pill.styleSheet()
    pill.update_text("Codes", theme.SUCCESS)
    assert pill.text() == "Codes"
    assert theme.SUCCESS in pill.styleSheet()


def test_score_bar(host):
    bar = widgets.ScoreBar(host)
    assert bar.score == 0.0
    bar.set_score(7.5)
    assert bar.score == 7.5
    bar.animate_to(9)
    assert bar._anim is not None
    small = widgets.ScoreBar(host, blocks=5)
    assert small._blocks == 5


def test_block_colour_runs_red_to_green():
    low, high = widgets.block_color(0), widgets.block_color(9)
    assert low.red() > low.green(), "the bottom of the scale should read red"
    assert high.green() > high.red(), "the top of the scale should read green"
    assert widgets.block_color(0, blocks=5).red() == low.red()


def test_widgets_paint_offscreen(host):
    """Actually render them: a paintEvent typo is not a UI-only problem."""
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import QVBoxLayout
    layout = QVBoxLayout(host)
    bar = widgets.ScoreBar(host)
    bar.set_score(6.5)
    layout.addWidget(bar)
    layout.addWidget(widgets.PillBadge("X", theme.ACCENT, host))
    overlay = widgets.LoadingOverlay(host)
    overlay.show_message("Working")
    host.show()
    pixmap = QPixmap(host.size())
    host.render(pixmap)
    assert not pixmap.isNull()
    overlay.hide_overlay()
    host.hide()


# ---------------------------------------------------------------------------
# The errata dialog
# ---------------------------------------------------------------------------

def test_the_dialog_builds_the_url_from_what_was_typed(qapp):
    from common.ui.errata_dialog import ErrataDialog
    dialog = ErrataDialog(app="exam-sim", item_id="ex_017",
                          item_text="Which primitive returns expectations?")
    assert dialog._open_btn.isEnabled() is False, (
        "a report with no description is not a report")
    dialog._why.setPlainText("Both answers are defensible.")
    assert dialog._open_btn.isEnabled() is True
    dialog._fix.setPlainText("Drop option B.")
    dialog._severity.setCurrentIndex(
        list(errata.SEVERITIES).index("misleading"))

    from urllib.parse import parse_qs, urlparse
    fields = {k: v[0] for k, v in parse_qs(urlparse(dialog.build_url()).query).items()}
    assert fields["quote"] == "Which primitive returns expectations?"
    assert fields["why_wrong"] == "Both answers are defensible."
    assert fields["correction"] == "Drop option B."
    assert fields["severity"] == errata.SEVERITIES["misleading"]
    assert "ex_017" in fields["file"]
    dialog.deleteLater()


def test_issue_url_is_none_until_accepted(qapp):
    from common.ui.errata_dialog import ErrataDialog
    dialog = ErrataDialog(app="exam-sim", item_id="x")
    assert dialog.issue_url is None
    dialog._why.setPlainText("wrong")
    dialog._on_accept()
    assert dialog.issue_url and dialog.issue_url.startswith("https://github.com/")
    dialog.deleteLater()


def test_the_button_opens_the_dialog_and_emits_the_url(qapp, monkeypatch, host):
    from common.ui import errata_dialog as ed

    class _Accepted(ed.ErrataDialog):
        def exec(self):                             # noqa: A003 (Qt naming)
            self._why.setPlainText("the stated answer is wrong")
            self._on_accept()
            return ed.QDialog.DialogCode.Accepted

    monkeypatch.setattr(ed, "ErrataDialog", _Accepted)
    button = ed.ErrataButton(host, app="qiskit-dojo", open_browser=False)
    button.set_item("kata_07", "Build a Bell state.")
    seen: list[str] = []
    button.reported.connect(seen.append)

    url = button.report()
    assert url and "kata_07" in url
    assert seen == [url]


def test_the_button_emits_nothing_when_cancelled(qapp, monkeypatch, host):
    from common.ui import errata_dialog as ed

    class _Cancelled(ed.ErrataDialog):
        def exec(self):                             # noqa: A003 (Qt naming)
            return ed.QDialog.DialogCode.Rejected

    monkeypatch.setattr(ed, "ErrataDialog", _Cancelled)
    button = ed.ErrataButton(host, app="qiskit-dojo", open_browser=False)
    seen: list[str] = []
    button.reported.connect(seen.append)
    assert button.report() is None
    assert seen == []


def test_nothing_in_common_but_ui_imports_qt():
    """coach.py, dashboard.py and tools/ must stay usable with no Qt."""
    import ast
    for path in (ROOT / "common").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            assert not any(n.startswith("PyQt") for n in names), (
                f"{path.name} imports Qt at the top level of common/")

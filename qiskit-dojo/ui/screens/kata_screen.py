"""Kata screen for qiskit-dojo — task pane, code editor, run/grade loop."""
from __future__ import annotations

import common_path  # noqa: F401  (puts the repo root on sys.path)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QPlainTextEdit, QSplitter, QMessageBox,
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QFont, QFontMetricsF

from common.ui.errata_dialog import ErrataButton

from config import APP_DIR_NAME
from core.models import Kata, KataAttempt, RunResult
from ui import theme
from ui.widgets.code_editor import CodeEditor
from ui.widgets.feedback_row import ConfidenceStrip, MistakeRow
from workers.run_worker import RunWorker
from workers.review_worker import ReviewWorker
from persistence import (
    clip, confidence_prompt_enabled, is_flagged, log_confidence, log_mistake,
    make_mistake_entry, resolve_mistakes, set_confidence_prompt_enabled,
    set_mistake_cause, toggle_flag,
)

_FLAG_OFF_TEXT = "⚑ Flag for review"
_FLAG_ON_TEXT  = "⚑ Flagged for review"

_NO_RUN_ANSWER = "(gave up without a passing run)"


def _failure_headline(output: str) -> str:
    """The one line that says what went wrong, for the journal's your_answer.

    The harness puts ``FAILED: …`` / ``ERROR: …`` first; fall back to the
    first non-empty line so a timeout or a bare traceback still says something.
    """
    lines = [ln.strip() for ln in (output or "").splitlines() if ln.strip()]
    for line in lines:
        if line.startswith(("FAILED:", "ERROR:")):
            return line
    for line in lines:
        if not line.startswith("==="):
            return line
    return lines[0] if lines else _NO_RUN_ANSWER


def _solution_gist(code: str) -> str:
    """The reference solution minus comments/blank lines, as one line."""
    body = [ln.strip() for ln in (code or "").splitlines()
            if ln.strip() and not ln.strip().startswith("#")]
    return clip(" | ".join(body)) or "(see Reveal Solution)"


def _repolish(widget) -> None:
    """Re-evaluate the app stylesheet after an objectName change."""
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


class KataScreen(QWidget):
    kata_completed = pyqtSignal(object)     # KataAttempt
    session_ended  = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._kata: Kata | None = None
        self._attempt: KataAttempt | None = None
        self._run_worker: RunWorker | None = None
        self._review_worker: ReviewWorker | None = None
        self._flagged: bool = False
        self._confidence: int | None = None
        self._confidence_logged: bool = False
        self._mistake_logged: bool = False
        self._last_failure: str = ""
        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 16)
        root.setSpacing(10)

        top_row = QHBoxLayout()
        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        top_row.addWidget(self._progress_lbl)
        self._section_lbl = QLabel("")
        top_row.addWidget(self._section_lbl)
        self._diff_lbl = QLabel("")
        self._diff_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        top_row.addWidget(self._diff_lbl)
        top_row.addStretch()
        self._end_btn = QPushButton("End Session")
        self._end_btn.setObjectName("flat")
        self._end_btn.clicked.connect(self._on_end_session)
        top_row.addWidget(self._end_btn)
        root.addLayout(top_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, 1)

        # ---- left: task pane -------------------------------------------
        left = QFrame(); left.setObjectName("card")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 14, 16, 14)
        left_layout.setSpacing(10)

        self._title_lbl = QLabel("")
        self._title_lbl.setWordWrap(True)
        self._title_lbl.setStyleSheet(f"font-size: 17px; font-weight: bold; color: {theme.TEXT};")
        left_layout.addWidget(self._title_lbl)

        self._prompt_view = QPlainTextEdit()
        self._prompt_view.setReadOnly(True)
        self._prompt_view.setObjectName("output")
        self._prompt_view.setStyleSheet(
            f"QPlainTextEdit {{ background: transparent; border: none; "
            f"color: {theme.TEXT}; font-size: 13px; }}"
        )
        self._prompt_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        left_layout.addWidget(self._prompt_view, 3)

        self._hint_lbl = QLabel("")
        self._hint_lbl.setWordWrap(True)
        self._hint_lbl.setStyleSheet(f"font-size: 13px; color: {theme.WARNING};")
        self._hint_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._hint_lbl.hide()
        left_layout.addWidget(self._hint_lbl)

        self._review_view = QPlainTextEdit()
        self._review_view.setReadOnly(True)
        self._review_view.setPlaceholderText("Claude review feedback appears here…")
        self._review_view.setStyleSheet(
            f"QPlainTextEdit {{ background: {theme.SURFACE2}; border: 1px solid {theme.BORDER}; "
            f"border-radius: 6px; color: {theme.TEXT}; font-size: 12px; }}"
        )
        self._review_view.hide()
        left_layout.addWidget(self._review_view, 2)
        splitter.addWidget(left)

        # ---- right: editor over output ---------------------------------
        right_split = QSplitter(Qt.Orientation.Vertical)

        editor_frame = QFrame(); editor_frame.setObjectName("card")
        editor_layout = QVBoxLayout(editor_frame)
        editor_layout.setContentsMargins(8, 8, 8, 8)
        editor_layout.setSpacing(6)
        editor_lbl = QLabel("Your code")
        editor_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        editor_layout.addWidget(editor_lbl)
        self._editor = CodeEditor()
        editor_layout.addWidget(self._editor)
        right_split.addWidget(editor_frame)

        output_frame = QFrame(); output_frame.setObjectName("card")
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(8, 8, 8, 8)
        output_layout.setSpacing(6)
        out_header = QHBoxLayout()
        out_lbl = QLabel("Output")
        out_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        out_header.addWidget(out_lbl)
        out_header.addStretch()
        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {theme.TEXT_MUTED};")
        out_header.addWidget(self._status_lbl)
        output_layout.addLayout(out_header)
        self._output_view = QPlainTextEdit()
        self._output_view.setReadOnly(True)
        self._output_view.setObjectName("output")
        mono = QFont("JetBrains Mono", 10)
        mono.setStyleHint(QFont.StyleHint.Monospace)
        self._output_view.setFont(mono)
        self._output_view.setTabStopDistance(
            QFontMetricsF(mono).horizontalAdvance(" ") * 4
        )
        self._output_view.setPlaceholderText("Run your code to see results here.")
        output_layout.addWidget(self._output_view)
        right_split.addWidget(output_frame)
        right_split.setSizes([420, 220])
        splitter.addWidget(right_split)
        splitter.setSizes([380, 640])

        # ---- feedback rows (above the buttons, full width) ---------------
        # Asked BEFORE the first Run, so the rating can never be hindsight.
        self._conf_strip = ConfidenceStrip()
        self._conf_strip.rated.connect(self._on_confidence_rated)
        self._conf_strip.opted_out.connect(self._on_confidence_opt_out)
        root.addWidget(self._conf_strip)

        # Shown once a kata is given up on; the mistake itself is already
        # journalled by then, so this row is pure diagnosis and skippable.
        self._mistake_row = MistakeRow()
        self._mistake_row.logged.connect(self._on_mistake_logged)
        self._mistake_row.hide()
        root.addWidget(self._mistake_row)

        # ---- bottom buttons --------------------------------------------
        btn_row = QHBoxLayout()
        self._hint_btn = QPushButton("Hint")
        self._hint_btn.setObjectName("flat")
        self._hint_btn.clicked.connect(self._on_hint)
        btn_row.addWidget(self._hint_btn)

        self._reveal_btn = QPushButton("Reveal Solution")
        self._reveal_btn.setObjectName("flat")
        self._reveal_btn.clicked.connect(self._on_reveal)
        btn_row.addWidget(self._reveal_btn)

        self._review_btn = QPushButton("Claude Review")
        self._review_btn.setObjectName("flat")
        self._review_btn.clicked.connect(self._on_review)
        btn_row.addWidget(self._review_btn)

        self._flag_btn = QPushButton(_FLAG_OFF_TEXT)
        self._flag_btn.setObjectName("flat")
        self._flag_btn.setToolTip(
            "Toggle this kata on the shared review list (dojo_flagged.json)"
        )
        self._flag_btn.clicked.connect(self._on_flag)
        btn_row.addWidget(self._flag_btn)

        # "This kata is wrong" -> a prefilled GitHub issue.  The repository is
        # public, and without this the only route from noticing a bad kata to
        # fixing it is remembering it later, which nobody does.  open_browser
        # is off so the failure of QDesktopServices (a machine with no browser,
        # a bare X session, a container) is ours to report instead of silent.
        self._errata_btn = ErrataButton(app=APP_DIR_NAME, open_browser=False,
                                        text="⚠ Report a problem")
        self._errata_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._errata_btn.setAccessibleName("Report a problem with this kata")
        self._errata_btn.setAccessibleDescription(
            "Open a prefilled GitHub issue about this kata: a wrong test, a "
            "retired Qiskit API, an ambiguous prompt. Nothing is sent until "
            "you submit it on GitHub."
        )
        self._errata_btn.setToolTip(self._errata_btn.accessibleDescription())
        self._errata_btn.reported.connect(self._on_errata_reported)
        btn_row.addWidget(self._errata_btn)

        btn_row.addStretch()

        self._run_btn = QPushButton("Run  ▶")
        self._run_btn.setObjectName("accent")
        self._run_btn.clicked.connect(self._on_run)
        btn_row.addWidget(self._run_btn)

        self._next_btn = QPushButton("Skip →")
        self._next_btn.clicked.connect(self._on_next)
        btn_row.addWidget(self._next_btn)
        root.addLayout(btn_row)

    # ------------------------------------------------------------- public

    def show_kata(self, kata: Kata, index: int, total: int) -> None:
        self._kata = kata
        self._attempt = KataAttempt(kata=kata)
        self._progress_lbl.setText(f"Kata {index} of {total}")
        color = theme.SECTION_COLORS.get(kata.section, theme.ACCENT)
        self._section_lbl.setText(kata.section)
        self._section_lbl.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {color}; "
            f"border: 1px solid {color}; border-radius: 9px; padding: 1px 10px;"
        )
        self._diff_lbl.setText(kata.difficulty)
        self._title_lbl.setText(kata.title)
        self._prompt_view.setPlainText(kata.prompt)
        self._editor.setPlainText(kata.starter_code)
        self._output_view.clear()
        self._status_lbl.setText("")
        self._hint_lbl.hide()
        self._hint_lbl.setText("")
        self._review_view.hide()
        self._review_view.clear()
        self._confidence = None
        self._confidence_logged = False
        self._last_failure = ""
        self._mistake_logged = False        # set first: hiding the note field
                                            # re-emits, and the guard reads it
        self._conf_strip.reset()
        self._conf_strip.setVisible(self._confidence_prompt_on())
        self._mistake_row.reset()
        self._mistake_row.hide()
        self._hint_btn.setEnabled(bool(kata.hints))
        self._hint_btn.setText(f"Hint (0/{len(kata.hints)})" if kata.hints else "Hint")
        self._reveal_btn.setEnabled(True)
        self._next_btn.setText("Skip →")
        self._next_btn.setObjectName("")        # drop the "accent" look from a pass
        _repolish(self._next_btn)
        # Run / Skip / End Session stay disabled while a run is still in
        # flight (never the case when a button brought us here).
        self._set_run_in_flight(self._run_worker is not None)
        self._errata_btn.set_item(kata.id, f"{kata.title}\n\n{kata.prompt}")
        try:
            flagged = is_flagged(kata.id)
        except Exception:
            flagged = False
        self._set_flag_state(flagged)

    def is_flagged(self) -> bool:
        """Whether the current kata is on the review list (UI state)."""
        return self._flagged

    def _set_flag_state(self, flagged: bool) -> None:
        self._flagged = flagged
        if flagged:
            self._flag_btn.setText(_FLAG_ON_TEXT)
            self._flag_btn.setStyleSheet(
                f"QPushButton {{ color: {theme.WARNING}; font-weight: bold; }}"
            )
        else:
            self._flag_btn.setText(_FLAG_OFF_TEXT)
            self._flag_btn.setStyleSheet("")

    # ------------------------------------------------------------ actions

    def _set_run_in_flight(self, running: bool) -> None:
        """While the harness runs, Run / Skip / End Session are all disabled,
        so a result can never land on a different kata than it graded."""
        self._run_btn.setEnabled(not running)
        self._next_btn.setEnabled(not running)
        self._end_btn.setEnabled(not running)

    def _on_run(self) -> None:
        if self._kata is None or self._run_worker is not None:
            return
        attempt = self._attempt
        attempt.tries += 1
        self._conf_strip.freeze()       # rating is locked once you have run
        self._set_run_in_flight(True)
        self._status_lbl.setText("Running…")
        self._status_lbl.setStyleSheet(
            f"font-weight: bold; font-size: 13px; color: {theme.TEXT_MUTED};"
        )
        self._run_worker = RunWorker(self._editor.toPlainText(), self._kata.test_code, self)
        # Bind the attempt this run grades: should the screen have moved on
        # by the time the result arrives, the stale result is dropped.
        self._run_worker.finished_run.connect(
            lambda result, a=attempt: self._on_run_finished(a, result)
        )
        self._run_worker.failed.connect(
            lambda err, a=attempt: self._on_run_failed(a, err)
        )
        self._run_worker.finished.connect(self._clear_run_worker)
        self._run_worker.start()

    def _clear_run_worker(self) -> None:
        self._run_worker = None
        self._set_run_in_flight(False)

    def _on_run_finished(self, attempt: KataAttempt, result: RunResult) -> None:
        if attempt is not self._attempt:
            return                          # result for a kata we already left
        self._output_view.setPlainText(result.output)
        self._log_calibration(result.passed)
        if result.passed:
            self._attempt.passed = True
            self._status_lbl.setText(f"✓ PASSED  ({result.duration_secs:.1f}s)")
            self._status_lbl.setStyleSheet(
                f"font-weight: bold; font-size: 13px; color: {theme.SUCCESS};"
            )
            self._next_btn.setText("Next →")
            self._next_btn.setObjectName("accent")
            _repolish(self._next_btn)
            self._mistake_row.hide()
            self._resolve_mistake()
        else:
            label = {
                "user_error":  "✗ ERROR IN YOUR CODE",
                "test_failed": "✗ TESTS FAILED",
                "timeout":     "✗ TIMED OUT",
            }.get(result.phase, "✗ FAILED")
            self._status_lbl.setText(f"{label}  ({result.duration_secs:.1f}s)")
            self._status_lbl.setStyleSheet(
                f"font-weight: bold; font-size: 13px; color: {theme.ERROR};"
            )
            # Journal it straight away with no cause: iterating on a kata is
            # normal, so the "what went wrong?" row waits for Reveal Solution,
            # but the failure itself is never lost.
            self._last_failure = _failure_headline(result.output)
            self._journal_mistake(self._last_failure)

    def _on_run_failed(self, attempt: KataAttempt, err: str) -> None:
        if attempt is not self._attempt:
            return
        self._output_view.setPlainText(f"Harness error:\n{err}")
        self._status_lbl.setText("✗ HARNESS ERROR")
        self._status_lbl.setStyleSheet(
            f"font-weight: bold; font-size: 13px; color: {theme.ERROR};"
        )

    def _on_flag(self) -> None:
        if self._kata is None:
            return
        try:
            new_state = toggle_flag(self._kata)
        except Exception as e:
            QMessageBox.warning(self, "Flag for Review",
                                f"Could not update the review list:\n{e}")
            return
        self._set_flag_state(new_state)

    def _on_errata_reported(self, url: str) -> None:
        """Hand the prefilled issue URL to the system browser.

        Never blocks (``openUrl`` hands off to the desktop and returns at
        once) and never loses the report: when there is no browser to hand it
        to, the URL is shown so it can be copied somewhere that has one.
        """
        if not url:
            return
        try:
            opened = QDesktopServices.openUrl(QUrl(url))
        except Exception:
            opened = False
        if opened:
            return
        box = QMessageBox(self)
        box.setWindowTitle("Report a problem")
        box.setText("No browser could be opened. Copy this link and open it "
                    "anywhere you can reach GitHub:")
        box.setInformativeText(url)
        box.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        box.exec()

    def _on_hint(self) -> None:
        if self._kata is None or not self._kata.hints:
            return
        shown = min(self._attempt.hints_used + 1, len(self._kata.hints))
        self._attempt.hints_used = shown
        text = "\n".join(
            f"Hint {i + 1}: {h}" for i, h in enumerate(self._kata.hints[:shown])
        )
        self._hint_lbl.setText(text)
        self._hint_lbl.show()
        self._hint_btn.setText(f"Hint ({shown}/{len(self._kata.hints)})")
        if shown >= len(self._kata.hints):
            self._hint_btn.setEnabled(False)

    def _on_reveal(self) -> None:
        if self._kata is None:
            return
        btn = QMessageBox.question(
            self, "Reveal Solution",
            "Show the reference solution in the output pane?\n"
            "(You can still edit, run, and pass the kata afterwards.)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if btn != QMessageBox.StandardButton.Yes:
            return
        self._attempt.revealed_solution = True
        self._output_view.setPlainText(
            "=== Reference solution ===\n\n" + self._kata.solution_code
        )
        self._status_lbl.setText("Solution revealed")
        self._status_lbl.setStyleSheet(
            f"font-weight: bold; font-size: 13px; color: {theme.WARNING};"
        )
        if not self._attempt.passed:
            # Giving up is the honest "wrong answer" moment in a dojo, so this
            # is where the cause chips appear.  The output pane now holds the
            # solution, hence the headline comes from the last failed run
            # rather than from what is on screen.
            self._journal_mistake(self._last_failure or _NO_RUN_ANSWER)
            self._mistake_row.show()

    def _on_review(self) -> None:
        if self._kata is None or self._review_worker is not None:
            return
        self._review_btn.setEnabled(False)
        self._review_view.show()
        self._review_view.setPlainText("Asking Claude for a code review…")
        self._review_worker = ReviewWorker(self._kata, self._editor.toPlainText(), self)
        self._review_worker.reviewed.connect(self._on_reviewed)
        self._review_worker.failed.connect(self._on_review_failed)
        self._review_worker.finished.connect(self._clear_review_worker)
        self._review_worker.start()

    def _clear_review_worker(self) -> None:
        self._review_worker = None
        self._review_btn.setEnabled(True)

    def _on_reviewed(self, feedback: str) -> None:
        self._review_view.setPlainText(feedback)

    def _on_review_failed(self, err: str) -> None:
        self._review_view.hide()
        QMessageBox.warning(self, "Claude Review Unavailable", err)

    # ------------------------------------------- calibration + mistake journal

    def _confidence_prompt_on(self) -> bool:
        try:
            return confidence_prompt_enabled()
        except Exception:
            return True

    def confidence_value(self) -> int | None:
        """The rating chosen for the current kata, if any (UI state)."""
        return self._confidence

    def _on_confidence_rated(self, level: int) -> None:
        self._confidence = int(level)

    def _on_confidence_opt_out(self) -> None:
        self._confidence = None
        self._conf_strip.hide()
        try:
            set_confidence_prompt_enabled(False)
        except Exception:
            pass

    def _log_calibration(self, correct: bool) -> None:
        """Pair the pre-run rating with the first graded outcome, once."""
        if self._kata is None or self._confidence is None or self._confidence_logged:
            return
        self._confidence_logged = True
        try:
            log_confidence(self._kata.id, self._kata.section,
                           self._confidence, correct)
        except Exception:
            pass

    def _journal_mistake(self, your_answer: str) -> None:
        """Record (or refresh) this kata's open mistake, cause not yet known."""
        if self._kata is None:
            return
        entry = make_mistake_entry(
            kata_id=self._kata.id,
            category=self._kata.section,
            question=self._kata.title,
            your_answer=your_answer,
            correct_answer=_solution_gist(self._kata.solution_code),
        )
        try:
            log_mistake(entry)
        except Exception:
            return
        self._mistake_logged = True

    def _on_mistake_logged(self, cause, note: str) -> None:
        if not self._mistake_logged or self._kata is None:
            return
        try:
            set_mistake_cause(self._kata.id, cause, note)
        except Exception:
            pass

    def _resolve_mistake(self) -> None:
        """Passing closes every open journal row for this kata — including one
        opened in an earlier session, which is the whole point of `resolved`."""
        if self._kata is None:
            return
        try:
            resolve_mistakes(self._kata.id)
        except Exception:
            return
        self._mistake_logged = False

    def _on_next(self) -> None:
        if self._attempt is None:
            return
        if self._attempt.tries == 0 and not self._attempt.passed:
            # Skipping without ever running still counts as one failed try.
            self._attempt.tries = 1
        self.kata_completed.emit(self._attempt)

    def _on_end_session(self) -> None:
        btn = QMessageBox.question(
            self, "End Session",
            "End the session now? Completed katas will be saved.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if btn == QMessageBox.StandardButton.Yes:
            self.session_ended.emit()

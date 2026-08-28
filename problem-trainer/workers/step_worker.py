"""QThread worker for checking one derivation step with Claude."""
from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal
from core.models import Derivation, Step


class StepCheckWorker(QThread):
    checked = pyqtSignal(str, object)    # step_id, StepCheck
    failed  = pyqtSignal(str, str)       # step_id, error message

    def __init__(self, derivation: Derivation, step: Step, answer: str,
                 accepted_steps: list[Step] | None = None,
                 tries: int = 1, parent=None) -> None:
        super().__init__(parent)
        self._derivation = derivation
        self._step       = step
        self._answer     = answer
        self._accepted   = list(accepted_steps or [])
        self._tries      = tries

    def run(self) -> None:
        try:
            from ai.grader import check_step
            result = check_step(self._derivation, self._step, self._answer,
                                self._accepted, self._tries)
            self.checked.emit(self._step.step_id, result)
        except Exception as e:
            self.failed.emit(self._step.step_id, str(e))

"""QThread worker that runs user code + kata tests through the harness."""
from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal


class RunWorker(QThread):
    finished_run = pyqtSignal(object)          # RunResult
    failed = pyqtSignal(str)

    def __init__(self, user_code: str, test_code: str, parent=None) -> None:
        super().__init__(parent)
        self._user_code = user_code
        self._test_code = test_code

    def run(self) -> None:
        try:
            from core.runner import run_kata
            result = run_kata(self._user_code, self._test_code)
            self.finished_run.emit(result)
        except Exception as e:
            self.failed.emit(str(e))

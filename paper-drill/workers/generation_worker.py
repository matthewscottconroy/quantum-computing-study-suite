"""QThread worker for question generation."""
from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal
from core.models import DrillConfig, Question


class GenerationWorker(QThread):
    questions_ready = pyqtSignal(list)
    failed          = pyqtSignal(str)

    def __init__(self, config: DrillConfig, parent=None) -> None:
        super().__init__(parent)
        self._config = config

    def run(self) -> None:
        try:
            from ai.generator import generate_questions
            questions = generate_questions(self._config.paper_text, self._config.question_count)
            self.questions_ready.emit(questions)
        except Exception as e:
            self.failed.emit(str(e))

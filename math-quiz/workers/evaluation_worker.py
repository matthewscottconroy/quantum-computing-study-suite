"""EvaluationWorker — QThread that grades an answer without blocking the UI."""

from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal

from core.models import Question, Evaluation
from core.claude_client import evaluate_answer, EvaluationError
from ai.prompt_builder import build_evaluation_prompt


class EvaluationWorker(QThread):
    evaluation_ready = pyqtSignal(object)   # Evaluation
    error = pyqtSignal(str)

    def __init__(self, question: Question, answer: str, parent=None) -> None:
        super().__init__(parent)
        self._question = question
        self._answer = answer

    def run(self) -> None:
        try:
            prompt = build_evaluation_prompt(self._question, self._answer)
            evaluation: Evaluation = evaluate_answer(prompt)
            self.evaluation_ready.emit(evaluation)
        except EvaluationError as exc:
            self.error.emit(str(exc))
        except Exception as exc:
            self.error.emit(f"Unexpected error evaluating answer: {exc}")

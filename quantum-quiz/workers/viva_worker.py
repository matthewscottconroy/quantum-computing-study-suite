"""
VivaWorker — runs in a QThread to generate ONE viva follow-up probe question
derived from the user's actual answer to the question just graded.

Follow-ups reuse the ordinary question-generation contract ({"question","hints"}),
so the same Claude client and response parser handle them. Cap: one follow-up per
base question, and follow-ups never spawn follow-ups (enforced by MainWindow).
"""

from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal

from core.session import QuizSession
from core.models import Question, Evaluation
from core.claude_client import generate_question, GenerationError
from ai.prompt_builder import build_viva_probe_prompt
from qiskit_contexts import EMPTY_CONTEXT


class VivaWorker(QThread):
    question_ready = pyqtSignal(object, object)   # (Question, QiskitContext)
    error = pyqtSignal(str)

    def __init__(
        self,
        session: QuizSession,
        base_question: Question,
        user_answer: str,
        evaluation: Evaluation,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._session = session
        self._base_question = base_question
        self._user_answer = user_answer
        self._evaluation = evaluation

    def run(self) -> None:
        try:
            prompt = build_viva_probe_prompt(
                self._base_question, self._user_answer, self._evaluation
            )
            question: Question = generate_question(prompt)

            # Same subject; topic tagged so history/SRS can distinguish it.
            question.subject = self._base_question.subject
            question.topic = f"{self._base_question.topic} (viva follow-up)"
            question.difficulty = self._base_question.difficulty
            question.question_type = self._base_question.question_type

            self._session.record_generated(question)
            # No Qiskit context for probes — they derive from the user's answer.
            self.question_ready.emit(question, EMPTY_CONTEXT)

        except GenerationError as exc:
            self.error.emit(str(exc))
        except Exception as exc:
            self.error.emit(f"Unexpected error generating follow-up: {exc}")

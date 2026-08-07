"""QuestionWorker — QThread that generates a question without blocking the UI."""

from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal

from core.session import MathSession
from core.models import Question
from core.claude_client import generate_question, GenerationError
from ai.prompt_builder import build_generation_prompt


class QuestionWorker(QThread):
    question_ready = pyqtSignal(object)   # Question
    error = pyqtSignal(str)

    def __init__(self, session: MathSession, parent=None) -> None:
        super().__init__(parent)
        self._session = session

    def run(self) -> None:
        try:
            # Serve pre-loaded questions first (e.g. "Review Mistakes" requeue)
            if self._session._pending_questions:
                question = self._session._pending_questions.pop(0)
                self._session.record_generated(question)
                self.question_ready.emit(question)
                return

            subject, topic, difficulty, question_type = self._session.next_topic()
            prompt = build_generation_prompt(
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                question_type=question_type,
                previous_texts=self._session.previous_question_texts(),
            )
            question: Question = generate_question(prompt)
            question.subject = subject
            question.topic = topic
            question.difficulty = difficulty
            question.question_type = question_type
            self._session.record_generated(question)
            self.question_ready.emit(question)
        except GenerationError as exc:
            self.error.emit(str(exc))
        except Exception as exc:
            self.error.emit(f"Unexpected error generating question: {exc}")

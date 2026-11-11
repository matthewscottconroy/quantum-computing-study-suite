"""
QuestionWorker — runs in a QThread to keep the UI non-blocking.
Builds Qiskit context → assembles prompt → calls Claude → emits result.
"""

from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal

from quantum_study.quantum_quiz.core.session import QuizSession
from quantum_study.quantum_quiz.core.models import Question
from quantum_study.quantum_quiz.core.qiskit_bridge import build_context
from quantum_study.quantum_quiz.core.claude_client import generate_question, GenerationError
from quantum_study.quantum_quiz.ai.prompt_builder import build_generation_prompt
from quantum_study.quantum_quiz.qiskit_contexts import QiskitContext


class QuestionWorker(QThread):
    question_ready = pyqtSignal(object, object)   # (Question, QiskitContext)
    error = pyqtSignal(str)

    def __init__(self, session: QuizSession, parent=None) -> None:
        super().__init__(parent)
        self._session = session

    def run(self) -> None:
        try:
            # Serve pre-loaded questions first (e.g. "Review Mistakes" requeue)
            if self._session._pending_questions:
                question = self._session._pending_questions.pop(0)
                # Build a (potentially empty) Qiskit context for the existing question
                context: QiskitContext = build_context(
                    question.subject, question.topic
                )
                self._session.record_generated(question)
                self.question_ready.emit(question, context)
                return

            subject, topic, difficulty, question_type = self._session.next_topic()

            # Build Qiskit context (may be EMPTY_CONTEXT — never raises)
            context = build_context(subject, topic)

            # Assemble prompt and call Claude
            prompt = build_generation_prompt(
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                question_type=question_type,
                previous_texts=self._session.previous_question_texts(),
                context=context,
            )
            question: Question = generate_question(prompt)

            # Fill in metadata that the parser left blank
            question.subject = subject
            question.topic = topic
            question.difficulty = difficulty
            question.question_type = question_type

            self._session.record_generated(question)
            self.question_ready.emit(question, context)

        except GenerationError as exc:
            self.error.emit(str(exc))
        except Exception as exc:
            self.error.emit(f"Unexpected error generating question: {exc}")

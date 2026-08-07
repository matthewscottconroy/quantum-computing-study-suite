"""QuizSession — tracks config, stats, and SRS-weighted topic selection."""

from __future__ import annotations
import random

from core.models import QuizConfig, Question, Evaluation, QuestionRecord, SessionStats
from core.topics import TOPICS, DIFFICULTY_LEVELS, QUESTION_TYPES


class QuizSession:
    def __init__(self, config: QuizConfig) -> None:
        self.config = config
        self.stats = SessionStats()
        self._previous_texts: list[str] = []

        # Shuffle-then-cycle ensures every question type appears once per cycle
        # before any type repeats — prevents e.g. 4 circuit designs in a row.
        self._type_cycle: list[str] = []

        # Questions pre-loaded for the next fetch (used by "Review Mistakes").
        self._pending_questions: list[Question] = []

        # Load SRS weights once at session start to avoid repeated file I/O.
        try:
            from persistence import avg_scores_by_subject, avg_scores_by_topic
            self._subject_scores: dict[str, float] = avg_scores_by_subject()
            self._topic_scores: dict[str, float]   = avg_scores_by_topic()
        except Exception:
            self._subject_scores = {}
            self._topic_scores   = {}

    # ── Topic selection ───────────────────────────────────────────────────────

    def next_topic(self) -> tuple[str, str, str, str]:
        """Return (subject, topic, difficulty, question_type) with SRS weighting."""
        subjects  = self.config.subjects
        s_weights = [
            max(0.5, 2.0 - self._subject_scores.get(s, 5.0) * 0.15)
            for s in subjects
        ]
        subject = random.choices(subjects, weights=s_weights, k=1)[0]

        topics   = TOPICS[subject]
        t_weights = [
            max(0.5, 2.0 - self._topic_scores.get(f"{subject}::{t}", 5.0) * 0.15)
            for t in topics
        ]
        topic = random.choices(topics, weights=t_weights, k=1)[0]

        difficulty    = self._next_difficulty()
        question_type = self._next_type()
        return subject, topic, difficulty, question_type

    def _next_difficulty(self) -> str:
        """Adaptive: start at beginner, ramp based on session average score."""
        if self.config.difficulty:
            return self.config.difficulty
        answered = self.stats.answered
        if answered < 2:
            return "beginner"
        avg = self.stats.average_score
        if avg >= 8.0:
            return random.choice(["advanced", "advanced", "expert", "expert"])
        if avg >= 6.5:
            return random.choice(["intermediate", "advanced", "advanced"])
        if avg >= 5.0:
            return random.choice(["beginner", "intermediate", "intermediate", "advanced"])
        return random.choice(["beginner", "beginner", "intermediate"])

    def _next_type(self) -> str:
        """Cycle through all selected types in shuffled order before repeating."""
        if not self._type_cycle:
            pool = list(self.config.question_types)
            random.shuffle(pool)
            self._type_cycle = pool
        return self._type_cycle.pop(0)

    def previous_question_texts(self) -> list[str]:
        from config import PREVIOUS_QUESTION_DEDUP_WINDOW
        return self._previous_texts[-PREVIOUS_QUESTION_DEDUP_WINDOW:]

    # ── Recording ─────────────────────────────────────────────────────────────

    def record_generated(self, question: Question) -> None:
        self.stats.total_generated += 1
        self._previous_texts.append(question.text[:150])

    def record_answer(
        self,
        question: Question,
        answer: str,
        evaluation: Evaluation,
        elapsed_seconds: int = 0,
    ) -> None:
        self.stats.answered += 1
        qid = f"{question.subject}::{question.topic}"
        self.stats.history.append(
            QuestionRecord(
                question=question,
                user_answer=answer,
                evaluation=evaluation,
                question_id=qid,
                elapsed_seconds=elapsed_seconds,
            )
        )

    def record_skip(self) -> None:
        self.stats.skipped += 1

    # ── Progress ──────────────────────────────────────────────────────────────

    def is_complete(self) -> bool:
        return (self.stats.answered + self.stats.skipped) >= self.config.question_count

    def questions_remaining(self) -> int:
        attempted = self.stats.answered + self.stats.skipped
        return max(0, self.config.question_count - attempted)

    def question_number(self) -> int:
        return self.stats.answered + self.stats.skipped + 1

"""TrainerSession — tracks config, stats, and SRS-weighted problem sequencing."""

from __future__ import annotations
import random
from core.models import TrainerConfig, Problem, Attempt, SessionStats, ProblemCategory


class TrainerSession:
    def __init__(self, config: TrainerConfig) -> None:
        self.config = config
        self.stats = SessionStats()
        self._category_queue: list[ProblemCategory] = self._build_queue()

    def _build_queue(self) -> list[ProblemCategory]:
        try:
            from persistence import avg_scores_by_category
            avg_scores = avg_scores_by_category()
        except Exception:
            avg_scores = {}

        cats = self.config.categories
        # Weight: categories with lower avg scores appear more often.
        # Score 0 → weight 2.0;  Score 10 → weight 0.5
        weights = [max(0.5, 2.0 - avg_scores.get(cat.value, 5.0) * 0.15) for cat in cats]

        queue = random.choices(cats, weights=weights, k=self.config.problem_count)
        return queue

    def next_category(self) -> ProblemCategory:
        attempted = self.stats.total
        if attempted < len(self._category_queue):
            return self._category_queue[attempted]
        return random.choice(self.config.categories)

    def next_difficulty(self) -> str:
        if self.config.difficulty:
            return self.config.difficulty
        # Adaptive: lean harder if accuracy is high
        acc = self.stats.accuracy
        if self.stats.total < 2:
            return "beginner"
        if acc >= 0.8:
            return random.choice(["advanced", "advanced", "intermediate"])
        if acc >= 0.5:
            return random.choice(["intermediate", "intermediate", "beginner", "advanced"])
        return random.choice(["beginner", "beginner", "intermediate"])

    def record(self, attempt: Attempt) -> None:
        self.stats.total += 1
        self.stats.attempts.append(attempt)
        if attempt.is_correct:
            self.stats.correct += 1
        elif attempt.score >= 4:
            self.stats.partial += 1
        else:
            self.stats.wrong += 1

    def record_skip(self) -> None:
        self.stats.total += 1

    def is_complete(self) -> bool:
        return self.stats.total >= self.config.problem_count

    def problem_number(self) -> int:
        return self.stats.total + 1

"""MathSession: topic selection, type cycling, difficulty policy, accounting."""
from __future__ import annotations

from config import PREVIOUS_QUESTION_DEDUP_WINDOW
from core.models import Evaluation, Question, QuizConfig, SessionStats
from core.session import MathSession
from core.topics import QUESTION_TYPES, TOPICS

SUBJECTS = list(TOPICS)[:3]


def _config(**kw) -> QuizConfig:
    base = dict(subjects=SUBJECTS, difficulty="intermediate",
                question_types=QUESTION_TYPES[:3], question_count=4)
    base.update(kw)
    return QuizConfig(**base)


def _q(subject=SUBJECTS[0], topic=None, text="Q?") -> Question:
    return Question(subject=subject, topic=topic or TOPICS[subject][0],
                    difficulty="intermediate", question_type="calculation", text=text)


def _ev(score: int) -> Evaluation:
    return Evaluation(score=score, verdict="", feedback="", model_answer="")


def test_next_topic_respects_config():
    s = MathSession(_config())
    for _ in range(60):
        subject, topic, difficulty, qtype = s.next_topic()
        assert subject in SUBJECTS
        assert topic in TOPICS[subject]
        assert difficulty == "intermediate"
        assert qtype in QUESTION_TYPES[:3]


def test_type_cycle_covers_every_type_before_repeating():
    types = QUESTION_TYPES[:4]
    s = MathSession(_config(question_types=types))
    for _ in range(3):
        cycle = [s.next_topic()[3] for _ in types]
        assert sorted(cycle) == sorted(types)


def test_adaptive_difficulty_starts_at_beginner_then_ramps():
    s = MathSession(_config(difficulty=None, question_count=20))
    assert s.next_topic()[2] == "beginner"
    assert s.next_topic()[2] == "beginner"
    for _ in range(3):
        s.record_answer(_q(), "ans", _ev(10))
    assert s.next_topic()[2] in {"advanced", "expert"}


def test_accounting_and_completion():
    s = MathSession(_config(question_count=3))
    assert (s.question_number(), s.questions_remaining(), s.is_complete()) == (1, 3, False)
    s.record_answer(_q(), "a", _ev(9), elapsed_seconds=42)
    s.record_skip()
    assert (s.question_number(), s.questions_remaining(), s.is_complete()) == (3, 1, False)
    s.record_answer(_q(), "b", _ev(2))
    assert s.is_complete() and s.questions_remaining() == 0
    assert s.stats.answered == 2 and s.stats.skipped == 1
    rec = s.stats.history[0]
    assert rec.question_id == f"{SUBJECTS[0]}::{TOPICS[SUBJECTS[0]][0]}"
    assert rec.elapsed_seconds == 42 and rec.user_answer == "a"


def test_previous_question_texts_window():
    s = MathSession(_config())
    for i in range(PREVIOUS_QUESTION_DEDUP_WINDOW + 4):
        s.record_generated(_q(text=f"question {i} " + "x" * 300))
    prev = s.previous_question_texts()
    assert len(prev) == PREVIOUS_QUESTION_DEDUP_WINDOW
    assert prev[-1].startswith(f"question {PREVIOUS_QUESTION_DEDUP_WINDOW + 3} ")
    assert all(len(t) <= 150 for t in prev)
    assert s.stats.total_generated == PREVIOUS_QUESTION_DEDUP_WINDOW + 4


def test_session_stats_aggregates():
    stats = SessionStats()
    assert stats.average_score == 0.0
    s = MathSession(_config())
    s.record_answer(_q(SUBJECTS[0]), "", _ev(10))
    s.record_answer(_q(SUBJECTS[1]), "", _ev(4))
    s.record_answer(_q(SUBJECTS[0]), "", _ev(7))
    assert s.stats.average_score == 7.0
    assert s.stats.scores_by_subject() == {SUBJECTS[0]: [10, 7], SUBJECTS[1]: [4]}

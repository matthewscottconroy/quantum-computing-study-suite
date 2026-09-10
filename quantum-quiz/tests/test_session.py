"""QuizSession accounting (viva follow-ups are extras), topic selection, type cycling."""
from __future__ import annotations

from config import PREVIOUS_QUESTION_DEDUP_WINDOW
from core.models import Evaluation, Question, QuizConfig
from core.session import QuizSession
from core.topics import QUESTION_TYPES, TOPICS

SUBJECTS = list(TOPICS)[:3]


def _config(**kw) -> QuizConfig:
    base = dict(subjects=SUBJECTS, difficulty="intermediate",
                question_types=QUESTION_TYPES[:3], question_count=3)
    base.update(kw)
    return QuizConfig(**base)


def _q(subject=SUBJECTS[0], topic=None, text="Q?") -> Question:
    return Question(subject=subject, topic=topic or TOPICS[subject][0],
                    difficulty="intermediate", question_type="conceptual explanation", text=text)


def _ev(score: int) -> Evaluation:
    return Evaluation(score=score, verdict="", feedback="", model_answer="")


def test_followups_do_not_consume_base_question_count():
    s = QuizSession(_config(question_count=3, viva_mode=True))
    s.record_answer(_q(), "a1", _ev(9))
    assert (s.question_number(), s.questions_remaining()) == (2, 2)

    s.record_answer(_q(text="probe"), "follow-up answer", _ev(6), is_followup=True)
    # the follow-up is recorded in history/answered but not in progress
    assert s.stats.answered == 2 and s.followups_answered == 1
    assert len(s.stats.history) == 2
    assert (s.question_number(), s.questions_remaining(), s.is_complete()) == (2, 2, False)

    s.record_answer(_q(), "a2", _ev(8))
    s.record_answer(_q(text="probe 2"), "f2", _ev(5), is_followup=True)
    assert (s.question_number(), s.questions_remaining(), s.is_complete()) == (3, 1, False)

    s.record_skip()
    assert s.is_complete() and s.questions_remaining() == 0
    assert s.stats.answered == 4 and s.stats.skipped == 1 and s.followups_answered == 2
    assert s.stats.average_score == (9 + 6 + 8 + 5) / 4


def test_base_accounting_without_followups():
    s = QuizSession(_config(question_count=2))
    assert (s.question_number(), s.questions_remaining(), s.is_complete()) == (1, 2, False)
    s.record_answer(_q(), "a", _ev(3), elapsed_seconds=17)
    assert (s.question_number(), s.questions_remaining(), s.is_complete()) == (2, 1, False)
    s.record_skip()
    assert s.is_complete()
    rec = s.stats.history[0]
    assert rec.question_id == f"{SUBJECTS[0]}::{TOPICS[SUBJECTS[0]][0]}"
    assert rec.elapsed_seconds == 17 and rec.user_answer == "a"
    assert s.followups_answered == 0


def test_next_topic_respects_config():
    s = QuizSession(_config())
    for _ in range(60):
        subject, topic, difficulty, qtype = s.next_topic()
        assert subject in SUBJECTS
        assert topic in TOPICS[subject]
        assert difficulty == "intermediate"
        assert qtype in QUESTION_TYPES[:3]


def test_type_cycle_covers_every_type_before_repeating():
    types = list(QUESTION_TYPES)   # includes teach-back
    s = QuizSession(_config(question_types=types))
    for _ in range(3):
        cycle = [s.next_topic()[3] for _ in types]
        assert sorted(cycle) == sorted(types)


def test_adaptive_difficulty_starts_at_beginner_then_ramps():
    s = QuizSession(_config(difficulty=None, question_count=20))
    assert s.next_topic()[2] == "beginner"
    assert s.next_topic()[2] == "beginner"
    for _ in range(3):
        s.record_answer(_q(), "ans", _ev(10))
    assert s.next_topic()[2] in {"advanced", "expert"}


def test_previous_question_texts_window():
    s = QuizSession(_config())
    for i in range(PREVIOUS_QUESTION_DEDUP_WINDOW + 4):
        s.record_generated(_q(text=f"question {i} " + "x" * 300))
    prev = s.previous_question_texts()
    assert len(prev) == PREVIOUS_QUESTION_DEDUP_WINDOW
    assert prev[-1].startswith(f"question {PREVIOUS_QUESTION_DEDUP_WINDOW + 3} ")
    assert all(len(t) <= 150 for t in prev)
    assert s.stats.total_generated == PREVIOUS_QUESTION_DEDUP_WINDOW + 4

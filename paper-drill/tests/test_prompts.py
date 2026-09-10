"""Generation and grading prompt builders are well-formed (no API calls)."""
import json

from ai import generator, grader
from config import MAX_PAPER_CHARS, MODEL

QUESTIONS_JSON = json.dumps([{"index": 1, "text": "Q1?", "type": "factual"}])
GRADE_JSON = json.dumps({"score": 8, "feedback": "Good.", "model_answer": "Ideal."})


def test_generation_template_mentions_required_keys():
    user = generator._USER_TMPL.format(text="PAPER-BODY", n=3)
    assert "PAPER-BODY" in user
    assert "exactly 3 questions" in user
    for key in ('"index"', '"text"', '"type"'):
        assert key in user
    for q_type in ("factual", "conceptual", "derivation"):
        assert q_type in user
    assert generator._SYSTEM.strip()


def test_grading_template_mentions_required_keys():
    user = grader._USER_TMPL.format(context="CTX", question="WHY?", answer="BECAUSE")
    assert "CTX" in user and "WHY?" in user and "BECAUSE" in user
    for key in ('"score"', '"feedback"', '"model_answer"'):
        assert key in user
    assert grader._SYSTEM.strip()


def test_generate_questions_sends_well_formed_request(fake_claude):
    messages = fake_claude(QUESTIONS_JSON)
    generator.generate_questions("The paper text.", 4)

    assert len(messages.calls) == 1
    call = messages.calls[0]
    assert call["model"] == MODEL == "claude-sonnet-4-6"
    assert call["system"] == generator._SYSTEM
    assert call["max_tokens"] > 0
    assert len(call["messages"]) == 1
    assert call["messages"][0]["role"] == "user"
    content = call["messages"][0]["content"]
    assert "The paper text." in content
    assert "exactly 4 questions" in content


def test_generate_questions_truncates_paper(fake_claude):
    messages = fake_claude(QUESTIONS_JSON)
    head = "A" * MAX_PAPER_CHARS
    generator.generate_questions(head + "ZZZ_TAIL_MARKER", 2)

    content = messages.calls[0]["messages"][0]["content"]
    assert head in content
    assert "ZZZ_TAIL_MARKER" not in content


def test_grade_answer_sends_well_formed_request(fake_claude):
    messages = fake_claude(GRADE_JSON)
    grader.grade_answer("Paper ctx", "What is X?", "X is Y.")

    call = messages.calls[0]
    assert call["model"] == MODEL
    assert call["system"] == grader._SYSTEM
    assert call["max_tokens"] > 0
    content = call["messages"][0]["content"]
    assert "Paper ctx" in content
    assert "What is X?" in content
    assert "X is Y." in content


def test_grade_answer_truncates_context(fake_claude):
    messages = fake_claude(GRADE_JSON)
    grader.grade_answer("B" * MAX_PAPER_CHARS + "TAIL_MARK", "q", "a")
    assert "TAIL_MARK" not in messages.calls[0]["messages"][0]["content"]

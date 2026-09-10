"""Curriculum data shape and the subject → Qiskit-context routing built on it."""
from __future__ import annotations

from core.qiskit_bridge import build_context
from core.topics import DIFFICULTY_LEVELS, QUESTION_TYPES, SUBJECT_CONTEXT_MODE, TOPICS
from qiskit_contexts import EMPTY_CONTEXT, QiskitContext

EXPECTED_SUBJECT_COUNT = 11
EXPECTED_TOPIC_COUNT = 124
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _first_subject(mode: str) -> str:
    return next(s for s, m in SUBJECT_CONTEXT_MODE.items() if m == mode)


# ── curriculum ────────────────────────────────────────────────────────────────

def test_eleven_subjects_and_124_topics():
    assert len(TOPICS) == EXPECTED_SUBJECT_COUNT
    assert sum(len(t) for t in TOPICS.values()) == EXPECTED_TOPIC_COUNT


def test_every_subject_has_non_empty_unique_topics():
    for subject, topics in TOPICS.items():
        assert isinstance(subject, str) and subject.strip()
        assert isinstance(topics, list) and topics, subject
        assert all(isinstance(t, str) and t.strip() for t in topics), subject
        assert len(set(topics)) == len(topics), f"duplicate topic in {subject}"


def test_question_types_include_teach_back_and_difficulty_levels():
    assert "teach-back" in QUESTION_TYPES
    assert len(set(QUESTION_TYPES)) == len(QUESTION_TYPES) >= 5
    assert all(isinstance(t, str) and t.strip() for t in QUESTION_TYPES)
    assert DIFFICULTY_LEVELS == ["beginner", "intermediate", "advanced", "expert"]


def test_every_subject_has_a_context_mode():
    assert set(SUBJECT_CONTEXT_MODE) == set(TOPICS)
    assert set(SUBJECT_CONTEXT_MODE.values()) <= {"circuit", "hamiltonian", "statevector", None}
    assert SUBJECT_CONTEXT_MODE["Quantum Computing"] == "circuit"


# ── qiskit_bridge.build_context ───────────────────────────────────────────────

def test_circuit_mode_subject_returns_rendered_circuit():
    subject = _first_subject("circuit")
    ctx = build_context(subject, TOPICS[subject][0])
    assert isinstance(ctx, QiskitContext) and ctx.has_content()
    assert ctx is not EMPTY_CONTEXT
    assert isinstance(ctx.qasm_snippet, str) and "OPENQASM" in ctx.qasm_snippet
    assert isinstance(ctx.circuit_png, bytes) and ctx.circuit_png.startswith(PNG_MAGIC)

    ctx = build_context("Quantum Computing", "two-qubit gates: CNOT, CZ, SWAP, Toffoli")
    assert ctx.has_content() and ctx.qasm_snippet


def test_hamiltonian_mode_subject_returns_pauli_table():
    subject = _first_subject("hamiltonian")
    ctx = build_context(subject, TOPICS[subject][0])
    assert ctx.has_content()
    assert isinstance(ctx.hamiltonian_str, str) and ctx.hamiltonian_str.strip()


def test_statevector_mode_subject_returns_amplitude_table():
    subject = _first_subject("statevector")
    ctx = build_context(subject, TOPICS[subject][0])
    assert ctx.has_content()
    assert isinstance(ctx.statevector_table, str) and ctx.statevector_table.strip()


def test_unknown_subject_returns_empty_context():
    ctx = build_context("Underwater Basket Weaving", "knots")
    assert ctx is EMPTY_CONTEXT and not ctx.has_content()


def test_every_topic_with_a_context_mode_produces_content():
    # build_context swallows builder exceptions and falls back to EMPTY_CONTEXT,
    # so an empty result here means a builder crashed for that topic.
    failures = [
        (subject, topic)
        for subject, topics in TOPICS.items()
        if SUBJECT_CONTEXT_MODE.get(subject)
        for topic in topics
        if not build_context(subject, topic).has_content()
    ]
    assert failures == []


def test_has_content_ignores_prose_only():
    assert not QiskitContext(prose_description="words").has_content()
    assert QiskitContext(qasm_snippet="qreg q[1];").has_content()
    assert not EMPTY_CONTEXT.has_content()


# ── theme.subject_color ───────────────────────────────────────────────────────

def test_every_subject_gets_a_distinct_colour():
    from ui import theme
    assert len(theme._SUBJECT_PALETTE) >= len(TOPICS)
    colours = {subject: theme.subject_color(subject) for subject in TOPICS}
    assert len(set(colours.values())) == len(TOPICS), colours
    assert colours["Qiskit Certification (C1000-179)"] != colours["Abstract Algebra"]
    assert theme.subject_color("Unknown Subject") == theme._SUBJECT_PALETTE[0]

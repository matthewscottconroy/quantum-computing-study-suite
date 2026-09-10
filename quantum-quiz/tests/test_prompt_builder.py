"""Prompt builders (generation, evaluation incl. teach-back rubric, viva probe) are well-formed."""
from __future__ import annotations

from ai.prompt_builder import (
    build_evaluation_prompt,
    build_generation_prompt,
    build_viva_probe_prompt,
)
from core.models import Evaluation, Question
from core.topics import DIFFICULTY_LEVELS, QUESTION_TYPES, TOPICS
from qiskit_contexts import EMPTY_CONTEXT, QiskitContext

GENERATION_CONTRACT = ('Respond with ONLY valid JSON', '"question"', '"hints"')
EVALUATION_CONTRACT = (
    'Respond with ONLY valid JSON', '"score"', '"verdict"', '"feedback"',
    '"model_answer"', '"key_points_missed"', '"follow_up"',
)
CONTEXT_HEADER = "Qiskit context (use this artefact"


def _question(**kw) -> Question:
    base = dict(subject="Quantum Computing", topic="the no-cloning theorem",
                difficulty="intermediate", question_type="proof sketch",
                text="Sketch why an arbitrary unknown qubit state cannot be copied.")
    base.update(kw)
    return Question(**base)


def _evaluation(**kw) -> Evaluation:
    base = dict(score=7, verdict="Correct", feedback="Linearity argument was fine.",
                model_answer="Assume U|ψ⟩|0⟩ = |ψ⟩|ψ⟩ ...",
                key_points_missed=["inner-product contradiction", "unitarity"])
    base.update(kw)
    return Evaluation(**base)


# ── generation ────────────────────────────────────────────────────────────────

def test_generation_prompt_without_context():
    p = build_generation_prompt("Quantum Computing", "the no-cloning theorem",
                                "advanced", "proof sketch", [], EMPTY_CONTEXT)
    assert isinstance(p, str)
    assert all(n in p for n in GENERATION_CONTRACT)
    assert "Quantum Computing" in p and "the no-cloning theorem" in p
    assert "advanced" in p and "proof sketch" in p
    assert CONTEXT_HEADER not in p
    assert "(none yet)" in p
    assert "{{" not in p and "}}" not in p


def test_generation_prompt_embeds_each_context_kind():
    qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\nh q[0];\ncx q[0],q[1];'
    p = build_generation_prompt("Qiskit", "t", "beginner", "circuit design", [],
                                QiskitContext(qasm_snippet=qasm, prose_description="A Bell pair"))
    assert CONTEXT_HEADER in p and qasm in p and "A Bell pair" in p

    p = build_generation_prompt("Linear Algebra", "t", "beginner", "conceptual explanation", [],
                                QiskitContext(hamiltonian_str="ZZ  +1.0\nXI  -0.5"))
    assert CONTEXT_HEADER in p and "ZZ  +1.0" in p

    p = build_generation_prompt("Quantum Mechanics", "t", "beginner", "conceptual explanation", [],
                                QiskitContext(statevector_table="|00⟩ 0.707\n|11⟩ 0.707"))
    assert CONTEXT_HEADER in p and "|11⟩ 0.707" in p

    # prose alone is not content
    p = build_generation_prompt("Qiskit", "t", "beginner", "circuit design", [],
                                QiskitContext(prose_description="only prose"))
    assert CONTEXT_HEADER not in p


def test_generation_prompt_lists_previous_questions():
    prev = ["Define a qubit.", "What does CNOT do?"]
    p = build_generation_prompt("Qiskit", "t", "beginner", "circuit design", prev, EMPTY_CONTEXT)
    assert all(f"  - {q}" in p for q in prev)
    assert "(none yet)" not in p


def test_generation_prompt_teach_back_supplement():
    tb = build_generation_prompt("Quantum Computing", "the surface code", "intermediate",
                                 "teach-back", [], EMPTY_CONTEXT)
    other = build_generation_prompt("Quantum Computing", "the surface code", "intermediate",
                                    "conceptual explanation", [], EMPTY_CONTEXT)
    assert "bright undergraduate" in tb and "EXPLAIN" in tb
    assert "bright undergraduate" not in other


def test_generation_prompt_certification_supplement():
    cert = "Qiskit Certification (C1000-179)"
    p = build_generation_prompt(cert, TOPICS[cert][0], "beginner", "conceptual explanation",
                                [], EMPTY_CONTEXT)
    assert "SamplerV2" in p and "ASSOCIATE" in p


def test_generation_prompt_well_formed_for_every_subject_type_and_difficulty():
    for subject, topics in TOPICS.items():
        for qtype in QUESTION_TYPES:
            for difficulty in DIFFICULTY_LEVELS:
                p = build_generation_prompt(subject, topics[-1], difficulty, qtype, [], EMPTY_CONTEXT)
                assert subject in p and topics[-1] in p, (subject, qtype)
                assert all(n in p for n in GENERATION_CONTRACT), (subject, qtype)
                assert "{{" not in p


# ── evaluation ────────────────────────────────────────────────────────────────

def test_evaluation_prompt_carries_contract_and_inputs():
    q = _question()
    p = build_evaluation_prompt(q, "By linearity, cloning |+⟩ fails.")
    assert all(n in p for n in EVALUATION_CONTRACT)
    assert q.text in p and "By linearity, cloning |+⟩ fails." in p
    assert q.subject in p and q.topic in p and q.difficulty in p and q.question_type in p
    assert "Grading rubric" not in p
    assert "{{" not in p and "}}" not in p


def test_evaluation_prompt_teach_back_rubric():
    p = build_evaluation_prompt(_question(question_type="teach-back"), "Imagine a photocopier...")
    assert "Grading rubric" in p
    for criterion in ("Factual accuracy", "Completeness", "Analogy quality", "Appropriate level"):
        assert criterion in p
    assert all(n in p for n in EVALUATION_CONTRACT)


# ── viva probe ────────────────────────────────────────────────────────────────

def test_viva_probe_prompt_is_self_contained_and_reuses_generation_contract():
    q, ev = _question(), _evaluation()
    p = build_viva_probe_prompt(q, "my answer text", ev)
    assert all(n in p for n in GENERATION_CONTRACT)
    assert q.text in p and "my answer text" in p
    assert "7/10" in p and "Correct" in p and ev.feedback in p
    for point in ev.key_points_missed:
        assert f"  - {point}" in p
    assert "ONE" in p and "SELF-CONTAINED" in p
    assert q.difficulty in p
    assert "{{" not in p and "}}" not in p

    p = build_viva_probe_prompt(q, "ans", _evaluation(key_points_missed=[]))
    assert "(none noted)" in p

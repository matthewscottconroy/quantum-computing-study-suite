"""Problem generator registry. Each generator returns a Problem instance."""

from __future__ import annotations
from core.models import ProblemCategory, Problem


def generate(category: ProblemCategory, difficulty: str) -> Problem:
    """Dispatch to the correct generator module (lazy import to keep startup fast)."""
    if category == ProblemCategory.SINGLE_GATE_OUTPUT:
        from problems import single_gate as m
    elif category == ProblemCategory.GATE_SEQUENCE:
        from problems import gate_sequence as m
    elif category == ProblemCategory.MEASUREMENT_PROBS:
        from problems import measurement as m
    elif category == ProblemCategory.GATE_IDENTITY:
        from problems import gate_identity as m
    elif category == ProblemCategory.CIRCUIT_UNITARY:
        from problems import circuit_unitary as m
    elif category == ProblemCategory.ENTANGLEMENT:
        from problems import entanglement as m
    elif category == ProblemCategory.MULTI_QUBIT_OUTPUT:
        from problems import multi_qubit as m
    elif category == ProblemCategory.CIRCUIT_EQUIVALENCE:
        from problems import equivalence as m
    elif category == ProblemCategory.NOTATION_READING:
        from problems import notation as m
    elif category == ProblemCategory.CIRCUIT_COMPOSITION:
        from problems import composition as m
    elif category == ProblemCategory.NOISE_CHANNEL:
        from problems import noise as m
    elif category == ProblemCategory.CIRCUIT_EXPLANATION:
        from problems import circuit_explanation as m
    else:
        raise ValueError(f"Unknown category: {category}")
    return m.generate(difficulty)

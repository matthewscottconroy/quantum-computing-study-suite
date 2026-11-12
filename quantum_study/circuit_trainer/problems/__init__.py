"""Problem generator registry. Each generator returns a Problem instance."""

from __future__ import annotations
from quantum_study.circuit_trainer.core.models import ProblemCategory, Problem


def generate(category: ProblemCategory, difficulty: str) -> Problem:
    """Dispatch to the correct generator module (lazy import to keep startup fast)."""
    if category == ProblemCategory.SINGLE_GATE_OUTPUT:
        from quantum_study.circuit_trainer.problems import single_gate as m
    elif category == ProblemCategory.GATE_SEQUENCE:
        from quantum_study.circuit_trainer.problems import gate_sequence as m
    elif category == ProblemCategory.MEASUREMENT_PROBS:
        from quantum_study.circuit_trainer.problems import measurement as m
    elif category == ProblemCategory.GATE_IDENTITY:
        from quantum_study.circuit_trainer.problems import gate_identity as m
    elif category == ProblemCategory.CIRCUIT_UNITARY:
        from quantum_study.circuit_trainer.problems import circuit_unitary as m
    elif category == ProblemCategory.ENTANGLEMENT:
        from quantum_study.circuit_trainer.problems import entanglement as m
    elif category == ProblemCategory.MULTI_QUBIT_OUTPUT:
        from quantum_study.circuit_trainer.problems import multi_qubit as m
    elif category == ProblemCategory.CIRCUIT_EQUIVALENCE:
        from quantum_study.circuit_trainer.problems import equivalence as m
    elif category == ProblemCategory.NOTATION_READING:
        from quantum_study.circuit_trainer.problems import notation as m
    elif category == ProblemCategory.CIRCUIT_COMPOSITION:
        from quantum_study.circuit_trainer.problems import composition as m
    elif category == ProblemCategory.NOISE_CHANNEL:
        from quantum_study.circuit_trainer.problems import noise as m
    elif category == ProblemCategory.CIRCUIT_EXPLANATION:
        from quantum_study.circuit_trainer.problems import circuit_explanation as m
    else:
        raise ValueError(f"Unknown category: {category}")
    return m.generate(difficulty)

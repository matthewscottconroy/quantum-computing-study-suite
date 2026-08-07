"""Problem: ft_flag_fault_tolerance"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_flag_fault_tolerance',
    category='Fault Tolerance',
    difficulty='advanced',
    question='What is flag fault tolerance, and what problem does it solve?',
    choices=[
        "A single 'flag' ancilla qubit detects high-weight errors caused by faults in syndrome measurement circuits, without full code-state ancilla preparation",
        'Flag qubits replace the data qubits to reduce physical qubit count',
        'Flag fault tolerance uses multiple layers of error correction to flag when the threshold is exceeded',
        'A syndrome qubit that flags measurement errors by repeating the measurement twice',
    ],
    correct_index=0,
    explanation='Flag fault tolerance (Chamberland & Cross 2018): standard fault-tolerant methods require expensive code-state ancilla verification. A single flag qubit is entangled with the syndrome measurement circuit at strategic points. If a fault in the measurement circuit would cause a high-weight (hard-to-correct) error on data, the flag qubit catches it by becoming entangled with the error and flagging upon measurement. This allows fault-tolerant syndrome extraction with fewer physical qubits than Shor-style (one ancilla per stabilizer) or Steane-style (full code blocks) methods.',
    hints=[
        'A flag qubit is a lightweight sentinel that detects dangerous high-weight errors from few-fault events.',
    ],
    grade_mode=GradeMode.AUTO,
)

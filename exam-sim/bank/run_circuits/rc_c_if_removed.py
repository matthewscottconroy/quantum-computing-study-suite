"""Question: rc_c_if_removed"""
from core.models import Question

QUESTION = Question(
    id='rc_c_if_removed',
    section='Run circuits',
    question='A Qiskit 0.x snippet does conditional feed-forward:\n\n```python\nqc.measure(0, 0)\nqc.x(1).c_if(qc.clbits[0], 1)\n```\n\nWhat happens in Qiskit 2.x, and what replaces it?',
    options=[
        'AttributeError — c_if was removed in Qiskit 2.0; use `with qc.if_test((qc.clbits[0], 1)): qc.x(1)`',
        'It still works; c_if is merely deprecated and warns',
        'AttributeError — the replacement is qc.x(1, condition=(qc.clbits[0], 1))',
        'It works but is silently ignored on simulators that do not support dynamic circuits',
    ],
    correct_index=0,
    explanation='Instruction.c_if and InstructionSet.c_if were removed in Qiskit 2.0. Classical control is now expressed with the control-flow builders — if_test (with an optional .else_ block), while_loop, for_loop, switch — which produce real IfElseOp instructions that the transpiler and dynamic-circuit backends understand.',
    difficulty='hard',
)

"""Question: rc_initial_layout"""
from core.models import Question

QUESTION = Question(
    id='rc_initial_layout',
    section='Run circuits',
    question='The backend is a 5-qubit line. What does this print?\n\n```python\npm = generate_preset_pass_manager(optimization_level=1,\n                                  backend=backend,\n                                  initial_layout=[3, 4])\nisa = pm.run(qc)              # qc is a 2-qubit Bell circuit\nprint(isa.layout.final_index_layout())\n```',
    options=[
        '[3, 4] — the two virtual qubits were pinned to physical qubits 3 and 4',
        '[0, 1] — initial_layout is only a hint and the layout pass overrides it',
        '[3, 4, 0, 1, 2] — final_index_layout() always returns the full physical register',
        'TranspilerError — initial_layout must list every physical qubit',
    ],
    correct_index=0,
    explanation='initial_layout=[3, 4] maps virtual qubit 0 to physical 3 and virtual 1 to physical 4; the layout stage honours it instead of searching. final_index_layout() reports where the *original* circuit qubits ended up after routing — here [3, 4], since an adjacent pair needs no SWAPs. (initial_index_layout() is the one that returns the padded 5-entry permutation.)',
    difficulty='hard',
)

"""Question: vz_bloch_multivector"""
from core.models import Question

QUESTION = Question(
    id='vz_bloch_multivector',
    section='Visualization',
    question='Which function draws one Bloch sphere PER QUBIT for a multi-qubit state?\n\n```python\nfrom qiskit.quantum_info import Statevector\nstate = Statevector(qc)\n```',
    options=[
        'plot_bloch_multivector(state)',
        'plot_bloch_vector(state)',
        'plot_state_qsphere(state)',
        'state.to_bloch()',
    ],
    correct_index=0,
    explanation="plot_bloch_multivector computes each qubit's reduced state and renders one sphere per qubit. plot_bloch_vector draws a single sphere from explicit [x, y, z] coordinates, and the qsphere is one combined visualization of the full state, not per-qubit spheres.",
    difficulty='medium',
)

"""Question: vz_bloch_vector_input"""
from core.models import Question

QUESTION = Question(
    id='vz_bloch_vector_input',
    section='Visualization',
    question='What happens?\n\n```python\nfrom qiskit.quantum_info import Statevector\nfrom qiskit.visualization import plot_bloch_vector\n\nqc = QuantumCircuit(1)\nqc.h(0)\nplot_bloch_vector(Statevector(qc))\n```',
    options=[
        'It draws |+⟩ on the Bloch sphere',
        'It draws an arrow of length zero at the centre of the sphere',
        'It raises an error — plot_bloch_vector wants Bloch coordinates [x, y, z], not a state object',
        'It returns None after emitting a deprecation warning',
    ],
    correct_index=2,
    explanation='plot_bloch_vector takes three numbers — Cartesian [x, y, z], or [r, θ, φ] with coord_type="spherical" — and indexes them directly, so a two-amplitude Statevector fails on the missing third element. For state objects use plot_bloch_multivector(state), which reduces each qubit and draws one sphere per qubit.',
    difficulty='medium',
)

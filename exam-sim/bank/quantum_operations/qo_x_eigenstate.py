"""Question: qo_x_eigenstate"""
from core.models import Question

QUESTION = Question(
    id='qo_x_eigenstate',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector\n\na = QuantumCircuit(1)\na.h(0)\nb = QuantumCircuit(1)\nb.h(0)\nb.x(0)\nprint(Statevector(a) == Statevector(b))\n```',
    options=[
        'True — |+⟩ is a +1 eigenstate of X, so the extra X changes nothing',
        'False — X flips the state to |−⟩',
        'False — X reverses the order of the amplitudes',
        'True — X is the identity on any single-qubit state',
    ],
    correct_index=0,
    explanation='H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2. Applying X swaps the |0⟩ and |1⟩ amplitudes, which are equal, so the state is exactly unchanged: X|+⟩ = |+⟩ (eigenvalue +1). X is certainly not the identity in general — it flips |0⟩ to |1⟩.',
    difficulty='medium',
)

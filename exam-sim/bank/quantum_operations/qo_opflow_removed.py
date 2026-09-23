"""Question: qo_opflow_removed"""
from core.models import Question

QUESTION = Question(
    id='qo_opflow_removed',
    section='Quantum operations',
    question='A tutorial written for Qiskit 0.x contains this. What happens on Qiskit 2.x?\n\n```python\nfrom qiskit.opflow import X, Z\n\nH = (X ^ Z) + 2 * Z\n```',
    options=[
        'ModuleNotFoundError — qiskit.opflow was removed; build Hamiltonians with SparsePauliOp',
        'DeprecationWarning — opflow still works but will be dropped in a future release',
        'It works — opflow was renamed but kept importable through an alias',
        'ImportError — only the operator globals X and Z were removed, the module remains',
    ],
    correct_index=0,
    explanation="qiskit.opflow (along with qiskit.algorithms and qiskit.extensions) was removed in Qiskit 1.0, so the import fails outright with ModuleNotFoundError — there is no deprecation shim left in 2.x. The replacement is qiskit.quantum_info: `SparsePauliOp.from_list([('XZ', 1), ('IZ', 2)])`, using `^`/tensor for tensor products and `+` for sums.",
    difficulty='medium',
)

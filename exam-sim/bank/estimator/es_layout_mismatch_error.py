"""Question: es_layout_mismatch_error"""
from core.models import Question

QUESTION = Question(
    id='es_layout_mismatch_error',
    section='Estimator',
    question='What happens?\n\n```python\nqc  = QuantumCircuit(2)      # backend has 5 qubits\nisa = pm.run(qc)\nestimator.run([(isa, SparsePauliOp("ZZ"))]).result()\n```',
    options=[
        'It works — the unused backend qubits are simply ignored',
        'ValueError: the number of qubits of the circuit (5) does not match the number of qubits of the ()-th observable (2)',
        'QiskitError: cannot apply instruction with classical bits',
        'It works but every expectation value comes back as nan',
    ],
    correct_index=1,
    explanation='An observable must act on exactly as many qubits as the circuit it is paired with. After transpilation the ISA circuit is the full backend width, so a 2-qubit observable no longer fits and the pub is rejected before anything runs. obs.apply_layout(isa.layout) is the fix; this mismatch is the most common error when moving from a simulator to hardware.',
    difficulty='medium',
)

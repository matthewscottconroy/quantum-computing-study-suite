"""Question: es_apply_layout"""
from core.models import Question

QUESTION = Question(
    id='es_apply_layout',
    section='Estimator',
    question='Which line makes `obs` usable with the transpiled circuit in an estimator pub?\n\n```python\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nobs = SparsePauliOp("ZZ")\n\npm  = generate_preset_pass_manager(optimization_level=1, backend=backend)  # 5-qubit backend\nisa = pm.run(qc)\n```',
    options=[
        'isa_obs = obs.apply_layout(isa.layout)',
        'isa_obs = obs.apply_layout(backend.target)',
        'isa_obs = SparsePauliOp("III").tensor(obs)',
        'No change is needed — the estimator pads observables with identities automatically',
    ],
    correct_index=0,
    explanation='Transpiling widens the circuit to the device size and may permute qubits, so the observable has to be re-expressed on the same qubits. SparsePauliOp.apply_layout(TranspileLayout) does both jobs at once, turning "ZZ" into "IIIZZ" here. Manual padding is only right when the layout happens to be the identity, apply_layout wants a layout rather than a target, and an unmapped observable raises ValueError.',
    difficulty='hard',
)

"""Question: rc_pass_manager_run"""
from core.models import Question

QUESTION = Question(
    id='rc_pass_manager_run',
    section='Run circuits',
    question='Which line completes this modern Qiskit 2.x transpilation workflow?\n\n```python\nfrom qiskit.transpiler import generate_preset_pass_manager\n\npm = generate_preset_pass_manager(optimization_level=1,\n                                  basis_gates=["sx", "rz", "cx"])\n# --- which line goes here? ---\n```',
    options=[
        'isa_circuit = pm.run(qc)',
        'isa_circuit = pm.transpile(qc)',
        'isa_circuit = pm.execute(qc)',
        'isa_circuit = qc.transpile(pm)',
    ],
    correct_index=0,
    explanation='A preset pass manager transforms circuits through its run() method, returning the transpiled (ISA) circuit. There is no transpile()/execute() method on the pass manager, and QuantumCircuit has no transpile() method.',
    difficulty='medium',
)

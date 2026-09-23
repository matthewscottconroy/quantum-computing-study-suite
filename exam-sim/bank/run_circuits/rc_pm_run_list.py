"""Question: rc_pm_run_list"""
from core.models import Question

QUESTION = Question(
    id='rc_pm_run_list',
    section='Run circuits',
    question='What is the type of `out`?\n\n```python\npm = generate_preset_pass_manager(optimization_level=1, backend=backend)\nout = pm.run([qc_a, qc_b, qc_c])\n```',
    options=[
        'A list of three transpiled QuantumCircuits',
        'A single QuantumCircuit with the three circuits composed in sequence',
        'A PassManagerResult holding the three circuits',
        'A generator that transpiles each circuit lazily on iteration',
    ],
    correct_index=0,
    explanation='PassManager.run() accepts one circuit or an iterable of them; given a list it returns a list of transpiled circuits in the same order (transpiling them in parallel where possible). Reusing one pass manager across a batch is the standard pattern before handing the circuits to a primitive.',
    difficulty='easy',
)

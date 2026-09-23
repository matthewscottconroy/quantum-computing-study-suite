"""Question: rc_transpile_vs_pm"""
from core.models import Question

QUESTION = Question(
    id='rc_transpile_vs_pm',
    section='Run circuits',
    question='What is the relationship between these two snippets?\n\n```python\n# A\nfrom qiskit import transpile\nisa = transpile(qc, backend=backend, optimization_level=1, seed_transpiler=9)\n\n# B\nfrom qiskit.transpiler import generate_preset_pass_manager\npm = generate_preset_pass_manager(optimization_level=1, backend=backend, seed_transpiler=9)\nisa = pm.run(qc)\n```',
    options=[
        'They do the same work — transpile() is a convenience wrapper that builds the same preset pass manager; B is preferred because the pass manager is reusable and inspectable',
        'A is deprecated and raises a DeprecationWarning in Qiskit 2.x',
        'A produces an ISA circuit but B only translates gates without routing',
        'They differ: transpile() never expands the circuit to the full backend width, while pm.run() does',
    ],
    correct_index=0,
    explanation='transpile() constructs a preset pass manager internally and runs it, so with the same arguments and seed both paths return equivalent circuits (both expanded to the backend width and both routed). The pass-manager form is the recommended Qiskit 2.x style because you build it once, reuse it for many circuits, inspect .stages, and swap individual stages.',
    difficulty='medium',
)

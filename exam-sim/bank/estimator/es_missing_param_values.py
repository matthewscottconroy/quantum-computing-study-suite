"""Question: es_missing_param_values"""
from core.models import Question

QUESTION = Question(
    id='es_missing_param_values',
    section='Estimator',
    question='What happens?\n\n```python\ntheta = Parameter("t")\nqc = QuantumCircuit(1)\nqc.ry(theta, 0)\n\nStatevectorEstimator().run([(qc, "Z")]).result()\n```',
    options=[
        'ValueError: the number of values (0) does not match the number of parameters (1) for the circuit',
        'The free parameter defaults to 0, so ⟨Z⟩ comes back as 1.0',
        'It returns a symbolic expression in t',
        'QiskitError: cannot apply instruction with classical bits',
    ],
    correct_index=0,
    explanation='A pub must be self-contained: if the circuit still has free parameters, the pub needs a value for every one of them, either as a sequence or as a {Parameter: value} mapping. Nothing silently defaults to zero, and primitives never return symbolic results.',
    difficulty='medium',
)

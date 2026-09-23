"""Question: es_observable_types"""
from core.models import Question

QUESTION = Question(
    id='es_observable_types',
    section='Estimator',
    question='Three of these observable arguments are accepted inside an estimator pub; one raises `TypeError: Invalid observable type`. Which one FAILS?',
    options=[
        'SparsePauliOp("ZZ")',
        'Pauli("ZZ")',
        '{"ZZ": 0.5, "XX": 0.5}',
        'Operator.from_label("ZZ")',
    ],
    correct_index=3,
    explanation='Observables are coerced by ObservablesArray, which understands Pauli label strings, Pauli, SparsePauliOp and mappings of label to coefficient (plus nested lists of those). A dense Operator matrix is not a Pauli representation and is rejected — convert it first with SparsePauliOp.from_operator(op).',
    difficulty='hard',
)

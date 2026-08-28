"""Question: es_v1_removed"""
from core.models import Question

QUESTION = Question(
    id='es_v1_removed',
    section='Estimator',
    question='Which import works in Qiskit 2.x for a local, exact estimator primitive?',
    options=[
        'from qiskit.primitives import StatevectorEstimator',
        'from qiskit.primitives import Estimator',
        'from qiskit.utils import QuantumInstance',
        'from qiskit.algorithms import Estimator',
    ],
    correct_index=0,
    explanation='StatevectorEstimator is the reference V2 estimator. The V1 Estimator class was removed in Qiskit 2.0, QuantumInstance disappeared with qiskit.utils back in 1.0, and qiskit.algorithms was spun out of the main package entirely.',
    difficulty='medium',
)

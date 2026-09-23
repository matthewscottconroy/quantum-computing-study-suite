"""Question: es_trex_measure_mitigation"""
from core.models import Question

QUESTION = Question(
    id='es_trex_measure_mitigation',
    section='Estimator',
    question='Which single option switches on twirled readout error extinction (TREX) without touching resilience_level?',
    options=[
        'estimator.options.dynamical_decoupling.enable = True',
        'estimator.options.twirling.enable_gates = True',
        'estimator.options.execution.init_qubits = True',
        'estimator.options.resilience.measure_mitigation = True',
    ],
    correct_index=3,
    explanation='TREX lives under resilience.measure_mitigation: measurements are randomly bit-flipped (twirled) and corrected classically so readout bias averages away. twirling.enable_gates is Pauli twirling of the entangling layers, dynamical decoupling fills idle time with pulse sequences, and init_qubits merely resets qubits before each shot.',
    difficulty='hard',
)

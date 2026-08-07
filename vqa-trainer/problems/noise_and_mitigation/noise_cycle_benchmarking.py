"""Problem: noise_cycle_benchmarking"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_cycle_benchmarking',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question='What is cycle benchmarking and how does it differ from standard randomized benchmarking?',
    choices=[
        'Characterises the error per circuit cycle (layer) rather than per gate; applies random Pauli gates before/after each cycle to twirl noise into Pauli channels',
        'Benchmarks entire quantum circuits (cycles of gates) by running them many times and averaging',
        'Uses a cycle of all Clifford gates in sequence to characterise the full gate set simultaneously',
        'A variant of RB where the sequence length m cycles through fixed values rather than growing',
    ],
    correct_index=0,
    explanation='Cycle benchmarking (CB, Erhard et al. 2019) is designed for characterising the noise of full circuit cycles (layers), including parallel multi-qubit gate operations. Random Pauli twirling frames are inserted before and after each cycle to convert arbitrary noise to a Pauli channel, enabling efficient characterisation. CB directly measures the error per cycle (not per individual gate), which is more relevant for VQAs where circuits consist of layers. It also naturally handles correlated errors between qubits that interact in the same cycle.',
    hints=[
        "Cycle = one layer of the circuit; CB twirls each layer's noise independently.",
    ],
    grade_mode=GradeMode.MC,
)

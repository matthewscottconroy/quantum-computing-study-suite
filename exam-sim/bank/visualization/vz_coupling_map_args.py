"""Question: vz_coupling_map_args"""
from core.models import Question

QUESTION = Question(
    id='vz_coupling_map_args',
    section='Visualization',
    question='You want to sketch a hypothetical 5-qubit line device for which you have no Backend object. Which call works?',
    options=[
        'plot_coupling_map(5, [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]], [[0, 1], [1, 2], [2, 3], [3, 4]])',
        'plot_coupling_map(CouplingMap.from_line(5))',
        'plot_gate_map(CouplingMap.from_line(5))',
        'plot_coupling_map([[0, 1], [1, 2], [2, 3], [3, 4]])',
    ],
    correct_index=0,
    explanation='plot_coupling_map(num_qubits, qubit_coordinates, coupling_map) needs all three positional arguments — how many qubits, where to draw each one, and which pairs to connect — because without a backend nothing else knows the geometry. plot_gate_map is the backend-driven wrapper that fills those in for you.',
    difficulty='hard',
)

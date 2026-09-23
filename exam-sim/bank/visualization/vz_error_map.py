"""Question: vz_error_map"""
from core.models import Question

QUESTION = Question(
    id='vz_error_map',
    section='Visualization',
    question='What does plot_error_map(backend) add compared with plot_gate_map(backend)?',
    options=[
        'Nothing — it is an alias kept for backwards compatibility',
        'The layout the transpiler picked for a particular circuit',
        'Calibration data: qubits and links coloured by error rate, plus readout-error bars',
        'The pulse schedule of each native gate',
    ],
    correct_index=2,
    explanation='plot_error_map draws the same lattice as plot_gate_map but colours every qubit and every coupling by its measured error rate and adds a readout-error panel — which is how you choose good qubits before transpiling. The chosen layout is plot_circuit_layout, and neither function shows pulses.',
    difficulty='medium',
)

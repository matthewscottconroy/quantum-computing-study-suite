"""Question: vz_gate_map_input"""
from core.models import Question

QUESTION = Question(
    id='vz_gate_map_input',
    section='Visualization',
    question='What does this raise?\n\n```python\nfrom qiskit.visualization import plot_gate_map\n\nqc = QuantumCircuit(5)\nplot_gate_map(qc)\n```',
    options=[
        'Nothing — it draws the circuit as a graph',
        'A VisualizationError about missing qubit coordinates',
        'Nothing — it draws an empty 5-qubit lattice',
        'An AttributeError — plot_gate_map takes a BACKEND, not a circuit',
    ],
    correct_index=3,
    explanation='plot_gate_map(backend) reads the device coupling map and qubit coordinates to draw the physical qubit lattice, so it needs a BackendV2; a QuantumCircuit has no coupling_map attribute. To see where a circuit landed on the device, use plot_circuit_layout(transpiled_circuit, backend).',
    difficulty='medium',
)

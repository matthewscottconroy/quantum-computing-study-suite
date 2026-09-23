"""Question: rc_isa_num_qubits"""
from core.models import Question

QUESTION = Question(
    id='rc_isa_num_qubits',
    section='Run circuits',
    question='The backend has 5 qubits. What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.transpiler import generate_preset_pass_manager\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure_all()\n\npm = generate_preset_pass_manager(optimization_level=1, backend=backend)\nprint(pm.run(qc).num_qubits)\n```',
    options=[
        '5 — the ISA circuit is widened to the full backend register, with the unused qubits as idle ancillas',
        '2 — transpilation never changes the number of qubits',
        '3 — routing adds one ancilla per SWAP inserted',
        'It raises TranspilerError because the circuit is narrower than the backend',
    ],
    correct_index=0,
    explanation='Once a layout is applied, the circuit is defined on the physical register: FullAncillaAllocation/EnlargeWithAncilla pad it to the target width, so an ISA circuit for a 5-qubit backend always has 5 qubits. Use result.layout (initial_index_layout()/final_index_layout()) to see which physical qubits your virtual qubits landed on.',
    difficulty='medium',
)

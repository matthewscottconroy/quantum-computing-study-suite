"""Question: rc_opt0_trivial_layout"""
from core.models import Question

QUESTION = Question(
    id='rc_opt0_trivial_layout',
    section='Run circuits',
    question='The backend is a 5-qubit line with couplings (0,1), (1,2), (2,3), (3,4). What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.transpiler import generate_preset_pass_manager\n\nqc = QuantumCircuit(3)\nqc.cx(0, 2)\n\npm0 = generate_preset_pass_manager(optimization_level=0, backend=backend)\npm1 = generate_preset_pass_manager(optimization_level=1, backend=backend)\nprint(pm0.run(qc).count_ops()["cx"], pm1.run(qc).count_ops()["cx"])\n```',
    options=[
        '4 1 — level 0 uses a trivial layout so routing inserts a SWAP (3 extra CX); level 1 picks a layout where the pair is already adjacent',
        '1 1 — both levels produce the same circuit because routing is layout-independent',
        '1 4 — higher optimization levels add SWAPs to spread the circuit over more qubits',
        '4 4 — every preset level maps logical qubit i to physical qubit i',
    ],
    correct_index=0,
    explanation='Level 0 applies TrivialLayout (logical i -> physical i), so cx(0, 2) spans non-adjacent qubits and routing must insert a SWAP, which costs 3 extra CX for a total of 4. Levels 1-3 run a layout search (VF2/Sabre) that places the two interacting qubits on a coupled pair, leaving a single CX.',
    difficulty='hard',
)

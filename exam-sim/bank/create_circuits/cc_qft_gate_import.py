"""Question: cc_qft_gate_import"""
from core.models import Question

QUESTION = Question(
    id='cc_qft_gate_import',
    section='Create circuits',
    question='In Qiskit 2.x, which import gives the supported (non-deprecated) Quantum Fourier Transform construct?',
    options=[
        'from qiskit.circuit.library import QFTGate',
        'from qiskit.circuit.library import QFT',
        'from qiskit.aqua.components.qfts import Standard',
        'from qiskit import QFT',
    ],
    correct_index=0,
    explanation='QFTGate (or qiskit.synthesis.synth_qft_full for an explicit synthesis) is the current API. The QFT *class* in qiskit.circuit.library still imports but is deprecated as of Qiskit 2.1 and will be removed in 3.0. qiskit.aqua was removed years ago, and QFT was never exported from the top-level qiskit namespace.',
    difficulty='easy',
)

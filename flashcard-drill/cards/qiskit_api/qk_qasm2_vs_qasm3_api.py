"""Card: qk_qasm2_vs_qasm3_api"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_qasm2_vs_qasm3_api',
    category='Qiskit API',
    front='How do you serialise/deserialise circuits to OpenQASM in Qiskit 2.x?',
    back='qiskit.qasm2 and qiskit.qasm3 modules, each with dumps(qc)/dump(qc, f) and loads(str)/load(file).  (QuantumCircuit no longer has a .qasm() method.)  qasm3.loads additionally requires the qiskit_qasm3_import package.',
)

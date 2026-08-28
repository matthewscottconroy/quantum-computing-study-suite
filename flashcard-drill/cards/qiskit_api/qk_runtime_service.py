"""Card: qk_runtime_service"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_runtime_service',
    category='Qiskit API',
    front='How do you connect to IBM Quantum in qiskit-ibm-runtime (current API)?',
    back="service = QiskitRuntimeService(channel='ibm_quantum_platform', token=…) — the legacy 'ibm_quantum' channel is retired.  QiskitRuntimeService.save_account(...) stores credentials; service.backend(name) / service.least_busy() select a device.",
)

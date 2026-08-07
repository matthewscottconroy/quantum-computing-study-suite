"""Card: qo_platforms"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qo_platforms',
    category='Quantum Optics',
    front='Photonic quantum computing platforms',
    back='Xanadu (continuous-variable, Gaussian boson sampling, Borealis).  PsiQuantum (fusion-based, single-photon qubits).  Quandela, ID Quantique.  Advantages: room-temperature operation, long coherence, fiber compatibility.',
)

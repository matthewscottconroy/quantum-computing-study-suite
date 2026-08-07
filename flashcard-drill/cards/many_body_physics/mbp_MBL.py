"""Card: mbp_MBL"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='mbp_MBL',
    category='Many-Body Physics',
    front='Many-body localization (MBL)',
    back='In disordered 1D systems, thermalization can be prevented — eigenstates violate the eigenstate thermalization hypothesis.  Qubits in MBL systems retain coherence; relevant for quantum memory.',
)

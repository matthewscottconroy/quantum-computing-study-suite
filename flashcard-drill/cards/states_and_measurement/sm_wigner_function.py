"""Card: sm_wigner_function"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_wigner_function',
    category='States & Measurement',
    front='Wigner function: definition and quantum signature',
    back='W(x,p) is a quasi-probability distribution over phase space.  Negativity of W is a necessary condition for non-classical behavior and a resource for quantum advantage in continuous-variable computing.',
)

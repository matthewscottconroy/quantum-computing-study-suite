"""Card: cx_PH_collapse"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='cx_PH_collapse',
    category='Complexity',
    front='If NP ⊆ BQP, what does that imply about PH?',
    back="NP ⊆ BQP ⊆ PSPACE.  If P=BQP this would collapse PH, but NP ⊆ BQP alone doesn't collapse PH directly — it's just widely disbelieved",
)

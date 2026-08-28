"""Card: qk_parameters"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_parameters',
    category='Qiskit API',
    front='How do Parameter / ParameterVector work with assign_parameters?',
    back="theta = Parameter('θ'); qc.rx(theta, 0) builds a parameterised circuit; ParameterVector('p', n) gives an indexable family.  qc.assign_parameters({theta: 1.2}) returns a NEW bound circuit (pass inplace=True to mutate).  qc.num_parameters counts unbound parameters.",
)

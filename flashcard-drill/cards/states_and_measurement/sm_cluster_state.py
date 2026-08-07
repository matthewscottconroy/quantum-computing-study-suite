"""Card: sm_cluster_state"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_cluster_state',
    category='States & Measurement',
    front='Resource states for MBQC',
    back='Cluster (graph) states are the resource for measurement-based quantum computation.  Prepared by CZ gates on a lattice of |+⟩ states; single-qubit adaptive measurements drive computation.',
)

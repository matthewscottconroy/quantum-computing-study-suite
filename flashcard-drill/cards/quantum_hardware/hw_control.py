"""Card: hw_control"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_control',
    category='Quantum Hardware',
    front='Quantum control: superconducting vs trapped-ion',
    back='Superconducting: microwave pulses at GHz frequencies; gates in ~10–100 ns.  Trapped-ion: laser pulses at optical/UV frequencies; gates in ~10–1000 μs.',
)

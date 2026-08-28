"""Card: qk_hist_vs_dist"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_hist_vs_dist',
    category='Qiskit API',
    front='plot_histogram vs plot_distribution — difference?',
    back='plot_histogram shows raw COUNTS per bitstring; plot_distribution shows normalised quasi-/probabilities (bars sum to 1, can show negative quasi-probability bars).  Both live in qiskit.visualization and accept one dict or a list of dicts for comparison.',
)

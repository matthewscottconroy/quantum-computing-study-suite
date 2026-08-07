"""Problem: bos_open_cat_vs_surface"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_open_cat_vs_surface',
    category='Bosonic Codes',
    difficulty='advanced',
    question='Compare the cat qubit + repetition code approach to the surface code for near-term fault-tolerant quantum error correction. What are the main advantages and disadvantages of each?',
    choices=[],
    correct_index=-1,
    explanation='Cat qubit + repetition code advantages: (1) exploits noise bias to achieve very low logical error rates with few physical qubits (potentially 10–100 cat qubits per logical qubit vs ~1000 for surface code); (2) simpler outer code (1D repetition vs 2D surface); (3) passive error suppression via the Kerr/driven-dissipative stabilization. Disadvantages: (1) implementing non-trivial gates on cat qubits is harder — only biased-noise Clifford gates are efficient; (2) the noise model must actually be biased for the advantage to hold; (3) microwave cavity hardware required; (4) T gates still need distillation or bosonic magic states. Surface code advantages: (1) hardware-agnostic 2D nearest-neighbor connectivity; (2) highest known threshold (~1%); (3) well-understood universal gate set via lattice surgery + distillation. Disadvantages: large qubit overhead (~1000 physical per logical), T-gate factory dominates cost.',
    hints=[
        'Consider: qubit overhead, gate implementation, noise model requirements, and hardware compatibility.',
    ],
    grade_mode=GradeMode.CLAUDE,
)

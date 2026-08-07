"""Problem: ft_postselection"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_postselection',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='Post-selection is sometimes used in quantum error correction experiments. When is post-selection valid for fault-tolerant computation?',
    choices=[
        'Only in benchmarking and analysis — post-selection on no errors is not a scalable fault-tolerant strategy',
        'Always — post-selection is the standard approach in all fault-tolerant schemes',
        'Only for state preparation, not for gate operations',
        'Post-selection is equivalent to error correction and can be used interchangeably',
    ],
    correct_index=0,
    explanation='Post-selection (discarding runs where errors were detected) can demonstrate high-fidelity logical operations in experiments but is not a scalable fault-tolerant strategy: the fraction of accepted runs decreases exponentially in circuit depth, making long computations impossible. True fault tolerance requires error correction (keeping all runs and correcting errors) rather than post-selection (discarding bad runs). Post-selection is useful for characterizing code performance but not for running algorithms.',
    hints=[
        "Post-selection discards bad runs — this doesn't scale; error correction fixes them.",
    ],
    grade_mode=GradeMode.AUTO,
)

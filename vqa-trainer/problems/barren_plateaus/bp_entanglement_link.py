"""Problem: bp_entanglement_link"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_entanglement_link',
    category='Barren Plateaus',
    difficulty='advanced',
    question='Cerezo et al. (2021) showed a connection between barren plateaus and quantum entanglement. What is it?',
    choices=[
        'States with high entanglement entropy across a bipartition exhibit barren plateaus for global cost functions',
        'Entangled states always avoid barren plateaus',
        'Barren plateaus only occur for separable (product) states',
        'Entanglement does not affect the gradient landscape',
    ],
    correct_index=0,
    explanation='If the reduced state on any subsystem is close to maximally mixed (high entanglement entropy), global cost functions have exponentially small variance. This provides a geometric picture: barren plateaus correspond to states near the maximally entangled manifold, where information about the cost is lost.',
    hints=[
        'A maximally entangled state has a maximally mixed reduced state on any subsystem.',
    ],
    grade_mode=GradeMode.MC,
)

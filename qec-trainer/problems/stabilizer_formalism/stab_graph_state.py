"""Problem: stab_graph_state"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_graph_state',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='A graph state |G⟩ on vertex set V with edge set E is the unique stabilizer state stabilized by generators Kᵥ for each vertex v. What is Kᵥ?',
    choices=[
        'Kᵥ = Xᵥ ⊗ (⊗_{u ∈ N(v)} Zᵤ), where N(v) is the set of neighbors of v',
        'Kᵥ = Zᵥ ⊗ (⊗_{u ∈ N(v)} Xᵤ)',
        'Kᵥ = ⊗_{u ∈ N(v)} CZ_{vu}',
        'Kᵥ = Xᵥ ⊗ Xᵥ for every edge (v,u)',
    ],
    correct_index=0,
    explanation='Graph states are defined by Kᵥ = Xᵥ ⊗_{u∈N(v)} Zᵤ: apply X on the vertex qubit and Z on all its neighbors. They are prepared by starting all qubits in |+⟩ and applying CZ gates along each edge: |G⟩ = ∏_{(u,v)∈E} CZ_{uv} |+⟩^⊗|V|. Graph states are universal resources for measurement-based quantum computation.',
    hints=[
        'The stabilizer generator for a vertex involves X on that vertex and Z on all its graph neighbors.',
    ],
    grade_mode=GradeMode.AUTO,
)

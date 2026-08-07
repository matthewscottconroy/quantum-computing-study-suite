"""Problem: bos_gkp_magic_state"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_gkp_magic_state',
    category='Bosonic Codes',
    difficulty='advanced',
    question='Why can GKP codes implement the T gate more naturally than qubit codes?',
    choices=[
        'GKP codes can implement T via a non-Clifford displacement in phase space that is naturally available in the continuous-variable setting, without magic state distillation',
        'GKP codes have transversal T because the lattice structure satisfies the triply-even property',
        'T gates are Clifford operations in the GKP framework',
        'GKP codes use photon counting to implement T without ancilla states',
    ],
    correct_index=0,
    explanation="In the GKP encoding, the logical T gate corresponds to a shear transformation in phase space, which can be implemented by a physical Hamiltonian of the form q̂³ or via Gaussian operations combined with the GKP lattice structure. More practically, GKP magic states |T_GKP⟩ can be prepared more efficiently than qubit magic states because the oscillator's large Hilbert space and the continuous-variable nature allow direct fault-tolerant preparation via GKP error correction followed by teleportation. This potentially reduces the T-gate overhead compared to multi-round magic state distillation required for qubit codes.",
    hints=[
        'Continuous-variable (oscillator) systems have more native operations available than two-level qubits.',
    ],
    grade_mode=GradeMode.AUTO,
)

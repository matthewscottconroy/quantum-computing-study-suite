"""Problem: steane_z_stabilizers"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_z_stabilizers',
    category='Steane Code',
    difficulty='intermediate',
    question='The Z-type stabilizers of the Steane code have the same structure as the X-type stabilizers, using Z instead of X. What does a Z-type stabilizer detect?',
    choices=[
        'X (bit-flip) errors — a Z stabilizer anticommutes with X on any qubit in its support',
        'Z (phase-flip) errors — Z stabilizers detect Z errors directly',
        'Y errors only — Z stabilizers are insensitive to both X and Z individually',
        'Both X and Z errors simultaneously on the same qubit',
    ],
    correct_index=0,
    explanation='Each Z-type stabilizer is a product of Z operators on a subset of qubits. A Pauli X on qubit i anticommutes with Z on qubit i (XZ = -ZX), so a Z-stabilizer anticommutes with any X error on a qubit in its support — giving syndrome bit 1. Conversely, a Z error commutes with all Z-stabilizers (ZZ = ZZ, no sign flip) and thus cannot be detected by Z-type stabilizers. This is the CSS decoupling: Z stabilizers → X error syndromes; X stabilizers → Z error syndromes.',
    hints=[
        'XZ = -ZX but ZZ = ZZ; which error anticommutes with a Z stabilizer?',
    ],
    grade_mode=GradeMode.AUTO,
)

"""Problem: bos_cat_noise_model"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_cat_noise_model',
    category='Bosonic Codes',
    difficulty='advanced',
    question='For a cat qubit with coherent amplitude |α|², the bit-flip probability under single-photon loss rate κ over time t scales approximately as:',
    choices=[
        'p_X ≈ κt|α|²/2 — proportional to the mean photon number (polynomial in |α|²)',
        'p_X ≈ e^{-κt|α|²} — exponentially suppressed',
        'p_X ≈ (κt)² |α|⁴ — quadratic in both time and photon number',
        'p_X ≈ κt — independent of |α|',
    ],
    correct_index=0,
    explanation='Under single-photon loss (Lindblad operator √κ â), the bit-flip error of a cat qubit scales as p_X ≈ κt⟨â†â⟩/2 ≈ κt|α|²/2 to leading order in κt. This is polynomial (linear) in the mean photon number |α|². In contrast, the phase-flip probability scales as p_Z ≈ (1 - e^{-2κt|α|²})/2 ≈ κt|α|² for short times, but the key point is that for large |α|² and realistic κt, p_Z is exponentially suppressed relative to p_X: p_Z/p_X ~ e^{-2|α|²}. This exponential ratio is the noise bias that makes cat qubits attractive.',
    hints=[
        'Photon loss changes the mean photon number by 1; the bit-flip rate scales with ⟨n̂⟩ = |α|².',
    ],
    grade_mode=GradeMode.AUTO,
)

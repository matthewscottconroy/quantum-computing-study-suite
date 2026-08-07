"""Problem: bos_binomial_code"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_binomial_code',
    category='Bosonic Codes',
    difficulty='intermediate',
    question='The binomial code is a bosonic code that protects against photon loss. For a code protecting against up to L photon losses, the codewords use Fock states:',
    choices=[
        'Spaced L+1 apart in photon number: |0̄⟩ uses Fock states |0⟩, |L+1⟩, |2(L+1)⟩, … with binomial coefficients',
        'Only the vacuum |0⟩ and single-photon |1⟩ states',
        'Coherent superpositions of all Fock states up to |L⟩',
        'Only even Fock states for bit-flip protection',
    ],
    correct_index=0,
    explanation='The binomial code (Michael et al. 2016) for protecting against L photon losses uses Fock states spaced (L+1) apart: the codewords are superpositions of |0⟩, |L+1⟩, |2(L+1)⟩, … with amplitudes given by binomial coefficients. The spacing ensures that losing up to L photons maps |0̄⟩ to states orthogonal to |1̄⟩ — making the error detectable. The binomial amplitudes ensure that the error operators E_L (photon loss of order L) satisfy the Knill-Laflamme conditions. These codes are important for microwave cavities where photon loss is the dominant error mechanism.',
    hints=[
        "Fock state spacing L+1 ensures L losses can't confuse |0̄⟩ and |1̄⟩.",
    ],
    grade_mode=GradeMode.AUTO,
)

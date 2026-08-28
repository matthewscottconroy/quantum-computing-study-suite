"""Question: es_vs_sampler"""
from core.models import Question

QUESTION = Question(
    id='es_vs_sampler',
    section='Estimator',
    question='You must compute the energy ⟨ψ(θ)|H|ψ(θ)⟩ of an ansatz for a Hamiltonian written as a SparsePauliOp. Which primitive is designed for this?',
    options=[
        'Estimator — it returns expectation values of observables directly',
        'Sampler — read the counts and the energy is the most frequent bitstring',
        'Either primitive returns expectation values; they are interchangeable',
        'Neither — expectation values require full state tomography',
    ],
    correct_index=0,
    explanation="The estimator's whole job is ⟨O⟩: you hand it (circuit, observable) pubs and get evs back. A sampler returns measurement data in the computational basis only; recovering ⟨H⟩ from it would require manual basis rotations and post-processing. Tomography is unnecessary for a known Pauli decomposition.",
    difficulty='easy',
)

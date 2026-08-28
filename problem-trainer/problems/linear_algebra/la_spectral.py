"""Problem: la_spectral — spectral decomposition facts and functions of operators."""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="la_spectral",
    topic="Linear Algebra & QM Math",
    title="Spectral Decomposition and Operator Functions",
    statement=(
        "Recall the spectral theorem: every Hermitian operator A on a finite-dimensional "
        "Hilbert space can be written A = Σᵢ λᵢ |i⟩⟨i| where {|i⟩} is an orthonormal "
        "eigenbasis and the λᵢ are its eigenvalues. For a function f, one defines "
        "f(A) = Σᵢ f(λᵢ) |i⟩⟨i|.\n\n"
        "Work through the following facts, ending with a concrete computation for the "
        "Pauli operator X = [[0,1],[1,0]]."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Prove that every eigenvalue of a Hermitian operator A is real, and that "
                "eigenvectors belonging to distinct eigenvalues are orthogonal."
            ),
            points=3,
            rubric=[
                "For reality: takes an eigenpair A|v⟩ = λ|v⟩ with |v⟩ ≠ 0 and computes "
                "⟨v|A|v⟩ two ways (or compares ⟨v|A|v⟩ with its conjugate), using "
                "A = A† to get λ⟨v|v⟩ = λ*⟨v|v⟩, hence λ = λ* since ⟨v|v⟩ > 0.",
                "For orthogonality: with A|v⟩ = λ|v⟩ and A|w⟩ = μ|w⟩, λ ≠ μ, evaluates "
                "⟨w|A|v⟩ both ways (acting right vs. left, using hermiticity and reality "
                "of μ) to get (λ − μ)⟨w|v⟩ = 0.",
                "Concludes ⟨w|v⟩ = 0 explicitly from λ ≠ μ; both conclusions clearly stated.",
            ],
            model_solution=(
                "Reality: let A|v⟩ = λ|v⟩ with |v⟩ ≠ 0. Then ⟨v|A|v⟩ = λ⟨v|v⟩. Taking the "
                "conjugate, ⟨v|A|v⟩* = ⟨v|A†|v⟩ = ⟨v|A|v⟩ since A = A†, so ⟨v|A|v⟩ is real; "
                "hence λ⟨v|v⟩ = λ*⟨v|v⟩ and since ⟨v|v⟩ > 0 we get λ = λ*.\n\n"
                "Orthogonality: let A|v⟩ = λ|v⟩ and A|w⟩ = μ|w⟩ with λ ≠ μ. Then "
                "⟨w|A|v⟩ = λ⟨w|v⟩. Acting on the left instead, ⟨w|A = ⟨w|A† = (A|w⟩)† = μ*⟨w| "
                "= μ⟨w| (μ real by the first part), so ⟨w|A|v⟩ = μ⟨w|v⟩. Subtracting: "
                "(λ − μ)⟨w|v⟩ = 0, and λ ≠ μ forces ⟨w|v⟩ = 0."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "Compute the spectral decomposition of X = [[0,1],[1,0]]: give its "
                "eigenvalues, normalised eigenvectors, and write X = Σᵢ λᵢ|i⟩⟨i| "
                "explicitly as a sum of outer products."
            ),
            points=3,
            rubric=[
                "Finds eigenvalues +1 and −1 (e.g. from det(X − λI) = λ² − 1 = 0).",
                "Finds the normalised eigenvectors |+⟩ = (|0⟩+|1⟩)/√2 for λ = +1 and "
                "|−⟩ = (|0⟩−|1⟩)/√2 for λ = −1.",
                "Writes X = |+⟩⟨+| − |−⟩⟨−| (or the equivalent explicit 2×2 matrices "
                "½[[1,1],[1,1]] − ½[[1,−1],[−1,1]]) and it is correct.",
            ],
            model_solution=(
                "det(X − λI) = λ² − 1 = 0, so λ = ±1. For λ = +1: (X − I)v = 0 gives "
                "v₀ = v₁, so |+⟩ = (|0⟩ + |1⟩)/√2. For λ = −1: v₀ = −v₁, so "
                "|−⟩ = (|0⟩ − |1⟩)/√2. Hence\n"
                "X = (+1)|+⟩⟨+| + (−1)|−⟩⟨−| = ½[[1,1],[1,1]] − ½[[1,−1],[−1,1]], "
                "which indeed equals [[0,1],[1,0]]."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Using the spectral decomposition from (b), compute (i) exp(iθX) and show "
                "it equals cos(θ)·I + i·sin(θ)·X, and (ii) a square root √X, i.e. an "
                "operator whose square is X. Give √X explicitly."
            ),
            points=4,
            rubric=[
                "Applies f(X) = f(1)|+⟩⟨+| + f(−1)|−⟩⟨−| for both functions.",
                "For exp: exp(iθX) = e^{iθ}|+⟩⟨+| + e^{−iθ}|−⟩⟨−|; regroups using "
                "|+⟩⟨+| + |−⟩⟨−| = I and |+⟩⟨+| − |−⟩⟨−| = X together with Euler's formula "
                "to get cos(θ)I + i sin(θ)X.",
                "For the root: uses √1 = 1 and a chosen branch √(−1) = i to get "
                "√X = |+⟩⟨+| + i|−⟩⟨−| = ½[(1+i)I + (1−i)X], i.e. the matrix "
                "½[[1+i, 1−i],[1−i, 1+i]] (any valid branch/answer whose square is X "
                "earns credit).",
                "Verifies (or clearly argues) that the claimed root squares to X, e.g. "
                "because (√X)² = 1·|+⟩⟨+| + i²·... — more precisely squaring the spectral "
                "form gives 1|+⟩⟨+| + (−1)|−⟩⟨−| = X since the projectors are orthogonal.",
            ],
            model_solution=(
                "(i) exp(iθX) = e^{iθ·1}|+⟩⟨+| + e^{iθ·(−1)}|−⟩⟨−|. Using Euler's formula "
                "and P₊ + P₋ = I, P₊ − P₋ = X (with P± the two projectors):\n"
                "exp(iθX) = cosθ (P₊ + P₋) + i sinθ (P₊ − P₋) = cos(θ)I + i sin(θ)X.\n\n"
                "(ii) Choose the branch √1 = 1, √(−1) = i. Then "
                "√X = 1·|+⟩⟨+| + i·|−⟩⟨−| = ½(1+i)I + ½(1−i)X = ½[[1+i, 1−i],[1−i, 1+i]].\n"
                "Check: since P₊P₋ = 0 and P±² = P±, (√X)² = 1²P₊ + i²P₋ = P₊ − P₋ = X. "
                "(Numerically: ½[[1+i,1−i],[1−i,1+i]] squared is exactly [[0,1],[1,0]].)"
            ),
        ),
    ],
)

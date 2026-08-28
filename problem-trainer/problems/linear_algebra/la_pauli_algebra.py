"""Problem: la_pauli_algebra — Pauli algebra and qubit rotations."""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="la_pauli_algebra",
    topic="Linear Algebra & QM Math",
    title="Pauli Algebra, Operator Expansion, and Rotations",
    statement=(
        "Let σ₁ = X, σ₂ = Y, σ₃ = Z be the Pauli matrices and n̂ = (n₁, n₂, n₃) a real "
        "unit vector, with n̂·σ = n₁X + n₂Y + n₃Z. These facts underpin single-qubit "
        "rotations, Bloch-sphere geometry, and Pauli-basis expansions used throughout "
        "quantum computing."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Prove the algebra relations: σᵢσⱼ + σⱼσᵢ = 2δᵢⱼ I for i,j ∈ {1,2,3} "
                "(you may verify the finitely many cases), and deduce that "
                "(n̂·σ)² = I for any real unit vector n̂."
            ),
            points=3,
            rubric=[
                "Establishes σᵢ² = I for each Pauli and anticommutation σᵢσⱼ = −σⱼσᵢ "
                "for i ≠ j (explicit matrix check of representative cases, or via "
                "σᵢσⱼ = δᵢⱼI + iεᵢⱼₖσₖ).",
                "Expands (n̂·σ)² = Σᵢⱼ nᵢnⱼ σᵢσⱼ and symmetrises: cross terms combine "
                "into anticommutators ½{σᵢ,σⱼ} = δᵢⱼI, killing i ≠ j terms.",
                "Concludes (n̂·σ)² = (Σᵢ nᵢ²) I = I using |n̂| = 1.",
            ],
            model_solution=(
                "Direct computation gives X² = Y² = Z² = I, and e.g. "
                "XY = iZ = −YX, YZ = iX = −ZY, ZX = iY = −XZ; hence "
                "{σᵢ,σⱼ} = σᵢσⱼ + σⱼσᵢ = 2δᵢⱼ I. Then\n"
                "(n̂·σ)² = Σᵢⱼ nᵢnⱼ σᵢσⱼ = ½ Σᵢⱼ nᵢnⱼ {σᵢ,σⱼ} (the antisymmetric part "
                "cancels against the symmetric coefficients nᵢnⱼ) = Σᵢⱼ nᵢnⱼ δᵢⱼ I "
                "= (n₁² + n₂² + n₃²) I = I."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "Show that any 2×2 Hermitian matrix A can be written uniquely as "
                "A = a₀I + a·σ with a₀ and a = (a₁,a₂,a₃) real, and give the explicit "
                "formulas a₀ = Tr(A)/2, aⱼ = Tr(σⱼA)/2."
            ),
            points=3,
            rubric=[
                "Notes {I, X, Y, Z} spans the (real) space of 2×2 Hermitian matrices — "
                "either by dimension count (4 real dimensions) or by explicit "
                "construction from the entries of A.",
                "Uses the trace orthogonality Tr(σᵢσⱼ) = 2δᵢⱼ and Tr(σⱼ) = 0 to project "
                "out the coefficients: a₀ = Tr(A)/2, aⱼ = Tr(σⱼA)/2.",
                "Shows the coefficients are real for Hermitian A (e.g. Tr(σⱼA) is real "
                "because σⱼA has trace equal to conjugate of Tr(Aσⱼ) = Tr(σⱼA)), and "
                "uniqueness follows from linear independence / the projection formulas.",
            ],
            model_solution=(
                "The four matrices {I, X, Y, Z} are linearly independent and Hermitian; "
                "the real vector space of 2×2 Hermitian matrices has real dimension 4 "
                "(a, d real on the diagonal, b = c* off-diagonal → 2 more real numbers), "
                "so they form a basis: A = a₀I + Σⱼ aⱼσⱼ. Multiplying by σⱼ and tracing, "
                "with Tr(σᵢσⱼ) = 2δᵢⱼ, Tr(σⱼ) = 0 and Tr(I) = 2:\n"
                "    a₀ = Tr(A)/2,   aⱼ = Tr(σⱼA)/2.\n"
                "Reality: for A, σⱼ Hermitian, Tr(σⱼA)* = Tr((σⱼA)†) = Tr(Aσⱼ) = Tr(σⱼA), "
                "so each aⱼ is real (similarly a₀). Uniqueness is immediate from these "
                "projection formulas."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Derive the rotation formula: for real θ,\n"
                "    exp(−iθ(n̂·σ)/2) = cos(θ/2) I − i sin(θ/2) (n̂·σ).\n"
                "Then evaluate it for n̂ = ẑ, θ = π and compare with the Pauli Z gate."
            ),
            points=4,
            rubric=[
                "Expands the exponential as a power series and splits even/odd terms.",
                "Uses (n̂·σ)² = I from part (a) so even powers give I·cos series and odd "
                "powers give (n̂·σ)·sin series, yielding cos(θ/2)I − i sin(θ/2)(n̂·σ).",
                "Evaluates n̂ = ẑ, θ = π: exp(−iπZ/2) = cos(π/2)I − i sin(π/2)Z = −iZ "
                "= diag(−i, i).",
                "States the comparison correctly: this equals Z up to the global phase "
                "−i (= e^{−iπ/2}), which is physically irrelevant.",
            ],
            model_solution=(
                "Let m = n̂·σ, so m² = I. Then\n"
                "exp(−iθm/2) = Σₖ (−iθ/2)ᵏ mᵏ / k! "
                "= Σ_even (−1)^{k/2}(θ/2)ᵏ/k! · I − i Σ_odd (−1)^{(k−1)/2}(θ/2)ᵏ/k! · m\n"
                "= cos(θ/2) I − i sin(θ/2) m.\n\n"
                "For n̂ = ẑ, θ = π: exp(−iπZ/2) = cos(π/2)I − i sin(π/2)Z = −iZ = "
                "diag(−i, +i). This is the Z gate up to the global phase e^{−iπ/2} = −i; "
                "global phases are unobservable, so Rz(π) implements Z."
            ),
        ),
    ],
)

"""Problem: qec_distance_proof — Knill–Laflamme conditions and code distance."""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="qec_distance_proof",
    topic="Error Correction",
    title="Error-Correction Conditions and a Distance Proof",
    statement=(
        "The Knill–Laflamme (KL) conditions: a code with projector P corrects an error "
        "set {Eᵢ} iff\n\n"
        "    P Eᵢ† Eⱼ P = cᵢⱼ P    for all i, j,\n\n"
        "with (cᵢⱼ) a Hermitian matrix. A code has distance d iff every Pauli operator "
        "E of weight ≤ d−1 satisfies P E P = c(E) P, while some weight-d Pauli violates "
        "this. This problem applies the conditions to the 3-qubit bit-flip code with "
        "codewords |0̄⟩ = |000⟩, |1̄⟩ = |111⟩."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Verify the KL conditions for the 3-qubit bit-flip code and the error "
                "set {I, X₁, X₂, X₃}: compute ⟨0̄|Eᵢ†Eⱼ|0̄⟩, ⟨1̄|Eᵢ†Eⱼ|1̄⟩ and "
                "⟨0̄|Eᵢ†Eⱼ|1̄⟩ for the required pairs and show they have the form cᵢⱼδ_kl "
                "on the codewords."
            ),
            points=4,
            rubric=[
                "Notes Eᵢ†Eⱼ for this set is either I (i = j) or XᵢXⱼ / a single Xᵢ "
                "(i ≠ j, one of them identity).",
                "Diagonal cases: ⟨0̄|I|0̄⟩ = ⟨1̄|I|1̄⟩ = 1 (cᵢᵢ = 1).",
                "Off-diagonal: XᵢXⱼ|000⟩ and Xᵢ|000⟩ are basis states of Hamming weight "
                "1 or 2, orthogonal to |000⟩ and |111⟩ ⇒ all matrix elements 0, and "
                "cross terms ⟨0̄|Eᵢ†Eⱼ|1̄⟩ = 0 since the images differ in at least one "
                "position. Hence cᵢⱼ = δᵢⱼ and KL holds (errors map code space to "
                "mutually orthogonal subspaces).",
            ],
            model_solution=(
                "The relevant products Eᵢ†Eⱼ are I, single Xᵢ, and pairs XᵢXⱼ.\n"
                "• i = j: Eᵢ†Eᵢ = I, and ⟨0̄|0̄⟩ = ⟨1̄|1̄⟩ = 1, ⟨0̄|1̄⟩ = 0: contributes "
                "cᵢᵢ = 1 on the code projector.\n"
                "• single Xᵢ: Xᵢ|000⟩ has Hamming weight 1 and Xᵢ|111⟩ weight 2 — both "
                "orthogonal to |000⟩ and |111⟩, so all matrix elements vanish.\n"
                "• XᵢXⱼ (i ≠ j): weight-2 image of |000⟩, weight-1 image of |111⟩ — "
                "again orthogonal to both codewords.\n"
                "So P Eᵢ†Eⱼ P = δᵢⱼ P: the KL matrix is the identity (a non-degenerate "
                "code), and the four errors send the code space into four mutually "
                "orthogonal 2-dimensional subspaces — measuring Z₁Z₂, Z₂Z₃ identifies "
                "which, and the error is undone."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "Show the bit-flip code FAILS the KL conditions for phase errors: "
                "exhibit the computation for E = Z₁ demonstrating P Z₁ P ≠ c P, and "
                "explain what this means operationally for an encoded superposition "
                "(α|0̄⟩ + β|1̄⟩)."
            ),
            points=3,
            rubric=[
                "Computes ⟨0̄|Z₁|0̄⟩ = +1 and ⟨1̄|Z₁|1̄⟩ = −1 (and ⟨0̄|Z₁|1̄⟩ = 0): "
                "P Z₁ P = Z̄ P-like, not proportional to P (the diagonal constants "
                "differ), violating KL.",
                "Identifies Z₁ (restricted to the code space) as acting like the logical "
                "Z̄: α|0̄⟩ + β|1̄⟩ → α|0̄⟩ − β|1̄⟩.",
                "Operational meaning: the error is invisible to the syndrome "
                "(Z₁ commutes with the Z-type checks) yet corrupts the encoded relative "
                "phase — an undetected logical error, so the code protects against X "
                "noise only.",
            ],
            model_solution=(
                "Z₁|000⟩ = |000⟩ and Z₁|111⟩ = −|111⟩, so ⟨0̄|Z₁|0̄⟩ = 1, "
                "⟨1̄|Z₁|1̄⟩ = −1, ⟨0̄|Z₁|1̄⟩ = 0. Thus P Z₁ P = |0̄⟩⟨0̄| − |1̄⟩⟨1̄|, which "
                "is not c·P for any scalar c (it is the logical Z̄ on the code space): "
                "the KL condition P E P = c P fails for E = Z₁.\n"
                "Operationally, Z₁ maps α|0̄⟩ + β|1̄⟩ to α|0̄⟩ − β|1̄⟩ while every "
                "stabilizer syndrome (Z₁Z₂, Z₂Z₃) stays +1 — the error is undetectable "
                "and has already changed the logical state. The bit-flip code corrects "
                "single X errors but no Z errors; protecting both needs a code like "
                "Shor's 9-qubit or Steane's 7-qubit code."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Prove the general relation between distance and correction power: a "
                "code of distance d corrects all Pauli errors of weight at most "
                "t = ⌊(d−1)/2⌋. (Hint: for two errors E, F of weight ≤ t, consider "
                "E†F and use the definition of distance via the KL conditions.)"
            ),
            points=3,
            rubric=[
                "Key step: if wt(E), wt(F) ≤ t then wt(E†F) ≤ 2t ≤ d − 1.",
                "Distance definition invoked correctly: d is the minimum weight of a "
                "Pauli E with P E P not proportional to P; equivalently every Pauli of "
                "weight ≤ d−1 satisfies P E P = c(E) P.",
                "Assembles the KL conditions: for all pairs E, F in the weight-≤t set, "
                "P E†F P = c(E†F) P, which is exactly the KL criterion for the set — "
                "hence a recovery operation exists correcting every weight-≤t error; "
                "conclusion t = ⌊(d−1)/2⌋ stated.",
            ],
            model_solution=(
                "Let the code have distance d, i.e. every Pauli operator G with "
                "wt(G) ≤ d − 1 satisfies P G P = c(G) P (and some weight-d Pauli "
                "violates it). Take the error set 𝔈 = {Pauli E : wt(E) ≤ t} with "
                "t = ⌊(d−1)/2⌋. For any E, F ∈ 𝔈, the product E†F is (up to phase) a "
                "Pauli supported on the union of their supports, so "
                "wt(E†F) ≤ wt(E) + wt(F) ≤ 2t ≤ d − 1. By the distance property, "
                "P E†F P = c(E†F) P for every pair — precisely the Knill–Laflamme "
                "conditions for 𝔈 (the matrix c is Hermitian since "
                "c(F†E) = c(E†F)*). KL then guarantees a recovery channel R with "
                "R(E ρ_code E†) = ρ_code for all E ∈ 𝔈: the code corrects all errors on "
                "up to t = ⌊(d−1)/2⌋ qubits. E.g. d = 3 ⇒ corrects any single-qubit "
                "error; d = 2 ⇒ t = 0, detection only."
            ),
        ),
    ],
)

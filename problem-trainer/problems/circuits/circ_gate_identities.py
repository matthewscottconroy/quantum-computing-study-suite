"""Problem: circ_gate_identities — gate identity derivations."""
from __future__ import annotations
from core.models import Problem, Part

PROBLEM = Problem(
    id="circ_gate_identities",
    topic="Circuits & Gates",
    title="Gate Identities: Conjugation and Basis Changes",
    statement=(
        "Prove the following standard circuit identities. Use matrix computation or "
        "action-on-basis-states arguments — both are acceptable if complete. "
        "Conventions: CNOT has qubit 1 as control, qubit 2 as target; "
        "CZ = diag(1,1,1,−1); H = (X+Z)/√2."
    ),
    parts=[
        Part(
            part_id="a",
            prompt=(
                "Prove HXH = Z and HZH = X. Conclude what H-conjugation does to an "
                "arbitrary Pauli product, and compute HYH."
            ),
            points=3,
            rubric=[
                "Proves HXH = Z and HZH = X (explicit 2×2 multiplication, or via "
                "H = (X+Z)/√2 with the anticommutation XZ = −ZX, or action on basis "
                "states/eigenvectors).",
                "Computes HYH = −Y (e.g. Y = iXZ ⇒ HYH = iHXH·HZH = iZX = −Y).",
                "States the conjugation rule: H swaps X↔Z (and negates Y), so "
                "H-conjugation of a Pauli string swaps X↔Z factor-wise on that qubit.",
            ],
            model_solution=(
                "With H = (X+Z)/√2 and X² = Z² = I, XZ = −ZX:\n"
                "HXH = ½(X+Z)X(X+Z) = ½(XXX + XXZ + ZXX + ZXZ) "
                "= ½(X + Z + Z − X) = Z,\n"
                "using ZXZ = −XZZ = −X. (Or directly as matrices: "
                "½[[1,1],[1,−1]][[0,1],[1,0]][[1,1],[1,−1]] = [[1,0],[0,−1]] = Z.)\n"
                "By the symmetry of H under X↔Z, the same computation gives HZH = X.\n"
                "Since XZ = −iY we have Y = iXZ, hence "
                "HYH = i(HXH)(HZH) = iZX = i(iY) = −Y.\n"
                "Rule: conjugating by H exchanges X and Z (and flips the sign of Y) on "
                "that qubit; for a Pauli string this acts factor-wise."
            ),
        ),
        Part(
            part_id="b",
            prompt=(
                "Prove that CNOT = (I⊗H)·CZ·(I⊗H), i.e. a CNOT is a CZ conjugated by "
                "Hadamards on the target. Explain in one sentence why CZ is symmetric "
                "under exchanging control and target while CNOT is not."
            ),
            points=3,
            rubric=[
                "Correct computation: for control |c⟩, CZ applies Z^c to the target, so "
                "(I⊗H)CZ(I⊗H) applies H Z^c H = X^c to the target — exactly CNOT. "
                "(Explicit 4×4 multiplication also fully acceptable.)",
                "Explicitly uses HZH = X (or the matrix identity) — the mechanism, not "
                "just the claim.",
                "Symmetry: CZ = diag(1,1,1,−1) puts a phase −1 only on |11⟩, which is "
                "invariant under swapping the qubits, so control/target are "
                "interchangeable; CNOT changes basis states asymmetrically.",
            ],
            model_solution=(
                "Block form: CZ = |0⟩⟨0|⊗I + |1⟩⟨1|⊗Z. Then\n"
                "(I⊗H) CZ (I⊗H) = |0⟩⟨0|⊗HIH + |1⟩⟨1|⊗HZH = |0⟩⟨0|⊗I + |1⟩⟨1|⊗X = CNOT,\n"
                "using H² = I and HZH = X. (Numerically, "
                "(I⊗H)·diag(1,1,1,−1)·(I⊗H) equals the CNOT matrix exactly.)\n"
                "CZ only imprints a −1 phase on |11⟩; the state |11⟩ and hence the gate "
                "are symmetric under qubit exchange, whereas CNOT maps |10⟩→|11⟩ but "
                "|01⟩→|01⟩, which is manifestly asymmetric."
            ),
        ),
        Part(
            part_id="c",
            prompt=(
                "Prove that (H⊗H)·CNOT₁₂·(H⊗H) = CNOT₂₁ — Hadamards on both qubits "
                "reverse the direction of a CNOT (control becomes target and vice versa)."
            ),
            points=4,
            rubric=[
                "A valid complete proof: explicit 4×4 computation, OR phase-kickback "
                "argument in the |±⟩ basis, OR stabilizer/Heisenberg argument "
                "(conjugation maps X₁→X₁X₂, Z₂→Z₁Z₂ etc., and H-conjugation swaps the "
                "roles so the transformed gate propagates X on qubit 2 to qubit 1).",
                "If using the |±⟩-basis argument: shows CNOT₁₂|x⟩|−⟩ = (−1)ˣ|x⟩|−⟩ "
                "(kickback) and tracks all four basis states |±⟩|±⟩ correctly.",
                "Clearly identifies the resulting operator as CNOT with control on "
                "qubit 2 and target on qubit 1 (maps |01⟩→|11⟩, |11⟩→|01⟩, fixes "
                "|00⟩, |10⟩).",
            ],
            model_solution=(
                "Heisenberg-picture proof. CNOT₁₂ conjugation acts on Pauli generators as "
                "X₁→X₁X₂, X₂→X₂, Z₁→Z₁, Z₂→Z₁Z₂. Conjugating by H⊗H swaps Xᵢ↔Zᵢ. So the "
                "composite U = (H⊗H)CNOT₁₂(H⊗H) sends\n"
                "Z₁ → (via H) X₁ → X₁X₂ → (via H) Z₁Z₂,\n"
                "X₂ → Z₂ → Z₁Z₂ → X₁X₂,\n"
                "X₁ → Z₁ → Z₁ → X₁,   Z₂ → X₂ → X₂ → Z₂.\n"
                "These are exactly the conjugation relations of CNOT₂₁ (control qubit 2: "
                "it propagates X₂ onto qubit 1 and Z₁ onto qubit 2). Since a Clifford "
                "unitary is fixed up to global phase by its action on the Pauli "
                "generators, U = CNOT₂₁; checking one basis state fixes the phase to +1. "
                "(Equivalently, kickback: in the |±⟩ basis the roles of control and "
                "target invert; the explicit product of matrices equals "
                "[[1,0,0,0],[0,0,0,1],[0,0,1,0],[0,1,0,0]] = CNOT₂₁ — verified "
                "numerically.)"
            ),
        ),
    ],
)

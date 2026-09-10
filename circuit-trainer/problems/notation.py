"""
Notation reading problems: parse Dirac notation or circuit shorthand.
Answer: MULTIPLE_CHOICE (auto-graded by string match).
"""

from __future__ import annotations
import random
from core.models import Problem, ProblemCategory, AnswerFormat

NOTATION_QUESTIONS: list[dict] = [
    # ── Beginner ──────────────────────────────────────────────────────────────
    {
        "difficulty": "beginner",
        "question": "What does the notation |ψ⟩ represent?",
        "correct": "A quantum state vector (ket vector) in Dirac notation",
        "choices": [
            "A quantum state vector (ket vector) in Dirac notation",
            "A classical probability distribution",
            "A bra vector (row vector)",
            "A measurement operator",
        ],
        "steps": [
            "|ψ⟩ is called a 'ket' in Dirac notation.",
            "It represents a column vector in a Hilbert space.",
            "Its dual (conjugate transpose) is the bra ⟨ψ|.",
        ],
        "concepts": ["Dirac notation", "ket vector", "Hilbert space"],
    },
    {
        "difficulty": "beginner",
        "question": "What is ⟨0|1⟩?",
        "correct": "0 (the states are orthogonal)",
        "choices": [
            "0 (the states are orthogonal)",
            "1 (inner product of basis states)",
            "1/√2",
            "Undefined",
        ],
        "steps": [
            "⟨0|1⟩ is the inner product of |0⟩ and |1⟩.",
            "|0⟩ = [1,0]ᵀ and |1⟩ = [0,1]ᵀ.",
            "⟨0|1⟩ = [1,0]·[0,1] = 0 — orthonormal basis.",
        ],
        "concepts": ["inner product", "orthogonality", "computational basis"],
    },
    {
        "difficulty": "beginner",
        "question": "What is the computational basis state |1⟩ as a column vector?",
        "correct": "[0, 1]ᵀ",
        "choices": ["[0, 1]ᵀ", "[1, 0]ᵀ", "[1, 1]ᵀ/√2", "[1, −1]ᵀ/√2"],
        "steps": [
            "|0⟩ = [1, 0]ᵀ (first basis vector).",
            "|1⟩ = [0, 1]ᵀ (second basis vector).",
            "This is the standard (computational) basis for a qubit.",
        ],
        "concepts": ["computational basis", "column vector", "qubit"],
    },
    {
        "difficulty": "beginner",
        "question": "What does |00⟩ mean in a 2-qubit system?",
        "correct": "Both qubits are in state |0⟩: |0⟩ ⊗ |0⟩",
        "choices": [
            "Both qubits are in state |0⟩: |0⟩ ⊗ |0⟩",
            "The number zero in binary",
            "A single qubit in a superposition",
            "The identity operator acting on two qubits",
        ],
        "steps": [
            "|00⟩ is shorthand for |0⟩ ⊗ |0⟩ (tensor product).",
            "In 4-dimensional space: [1,0,0,0]ᵀ.",
            "Qubit ordering convention: leftmost = qubit 0.",
        ],
        "concepts": ["multi-qubit notation", "tensor product", "basis states"],
    },
    # ── Intermediate ─────────────────────────────────────────────────────────
    {
        "difficulty": "intermediate",
        "question": "What does |+⟩ mean, and what is its column vector representation?",
        "correct": "(|0⟩ + |1⟩)/√2, column vector [1/√2, 1/√2]ᵀ",
        "choices": [
            "(|0⟩ + |1⟩)/√2, column vector [1/√2, 1/√2]ᵀ",
            "(|0⟩ − |1⟩)/√2, column vector [1/√2, −1/√2]ᵀ",
            "(|0⟩ + i|1⟩)/√2",
            "The +1 eigenstate of Z",
        ],
        "steps": [
            "|+⟩ = H|0⟩ = (|0⟩ + |1⟩)/√2.",
            "Column vector: [1/√2, 1/√2]ᵀ.",
            "It is the +1 eigenstate of X (not Z).",
        ],
        "concepts": ["|+⟩ state", "Hadamard", "X eigenstates"],
    },
    {
        "difficulty": "intermediate",
        "question": "In the expression ⟨ψ|A|ψ⟩, what does this compute?",
        "correct": "The expectation value of observable A in state |ψ⟩",
        "choices": [
            "The expectation value of observable A in state |ψ⟩",
            "The inner product of |ψ⟩ with itself",
            "The eigenvalue of A",
            "The matrix element A_{ψψ}",
        ],
        "steps": [
            "⟨ψ|A|ψ⟩ is a 'sandwich' of operator A between bra and ket.",
            "= Σᵢ pᵢ λᵢ where pᵢ = |⟨aᵢ|ψ⟩|² and λᵢ are eigenvalues.",
            "This is the expectation value (average measurement outcome).",
        ],
        "concepts": ["expectation value", "Dirac sandwich", "observables"],
    },
    {
        "difficulty": "intermediate",
        "question": "What does the tensor product notation |ψ⟩ ⊗ |φ⟩ represent?",
        "correct": "A composite system where subsystem 1 is in state |ψ⟩ and subsystem 2 is in state |φ⟩",
        "choices": [
            "A composite system where subsystem 1 is in state |ψ⟩ and subsystem 2 is in state |φ⟩",
            "The inner product of |ψ⟩ and |φ⟩",
            "The outer product |ψ⟩⟨φ|",
            "A superposition of |ψ⟩ and |φ⟩",
        ],
        "steps": [
            "⊗ is the tensor product — it combines two Hilbert spaces.",
            "If dim(V)=2, dim(W)=2, then dim(V⊗W)=4.",
            "A product state is separable; not all 2-qubit states factor this way.",
        ],
        "concepts": ["tensor product", "composite systems", "separability"],
    },
    {
        "difficulty": "intermediate",
        "question": "What is the commutator [X, Z] of the Pauli X and Z operators?",
        "correct": "[X, Z] = XZ − ZX = −2iY",
        "choices": [
            "[X, Z] = XZ − ZX = −2iY",
            "[X, Z] = 0 (they commute)",
            "[X, Z] = 2iY",
            "[X, Z] = I",
        ],
        "steps": [
            "XZ = [[0,1],[1,0]]·[[1,0],[0,-1]] = [[0,-1],[1,0]] = iY·(-1)... let's compute directly.",
            "XZ = [[0,-1],[1,0]], ZX = [[0,1],[-1,0]].",
            "[X,Z] = XZ − ZX = [[0,-1],[1,0]] − [[0,1],[-1,0]] = [[0,-2],[2,0]] = -2iY.",
        ],
        "concepts": ["commutator", "Pauli algebra", "anticommuting operators"],
    },
    {
        "difficulty": "intermediate",
        "question": "What is the bra ⟨ψ| corresponding to the ket |ψ⟩ = α|0⟩ + β|1⟩?",
        "correct": "⟨ψ| = α*⟨0| + β*⟨1|  (complex conjugate of coefficients)",
        "choices": [
            "⟨ψ| = α*⟨0| + β*⟨1|  (complex conjugate of coefficients)",
            "⟨ψ| = α⟨0| + β⟨1|  (same coefficients)",
            "⟨ψ| = −α⟨0| − β⟨1|",
            "⟨ψ| = β⟨0| + α⟨1|",
        ],
        "steps": [
            "The bra ⟨ψ| is the conjugate transpose (†) of the ket |ψ⟩.",
            "|ψ⟩ = [α, β]ᵀ, so ⟨ψ| = [α*, β*] (row vector with conjugated entries).",
            "Written in Dirac notation: ⟨ψ| = α*⟨0| + β*⟨1|.",
        ],
        "concepts": ["bra vector", "conjugate transpose", "Dirac notation"],
    },
    {
        "difficulty": "intermediate",
        "question": "What does it mean for a quantum state α|0⟩ + β|1⟩ to be normalised?",
        "correct": "|α|² + |β|² = 1",
        "choices": [
            "|α|² + |β|² = 1",
            "α + β = 1",
            "|α| + |β| = 1",
            "α² + β² = 0",
        ],
        "steps": [
            "Normalisation: ⟨ψ|ψ⟩ = 1.",
            "⟨ψ|ψ⟩ = α*α + β*β = |α|² + |β|² = 1.",
            "This ensures the total probability of measuring any outcome sums to 1.",
        ],
        "concepts": ["normalisation", "probability amplitudes", "Born rule"],
    },
    {
        "difficulty": "intermediate",
        "question": "What is a unitary operator U in terms of its adjoint U†?",
        "correct": "U†U = UU† = I  (U† is the inverse of U)",
        "choices": [
            "U†U = UU† = I  (U† is the inverse of U)",
            "U†U = 0",
            "U² = I  (U is its own inverse)",
            "U† = −U",
        ],
        "steps": [
            "A unitary operator satisfies U†U = UU† = I.",
            "This means U preserves inner products: ⟨Uφ|Uψ⟩ = ⟨φ|ψ⟩.",
            "All quantum gates are unitary (reversible, norm-preserving).",
        ],
        "concepts": ["unitary operator", "adjoint", "quantum gates"],
    },
    {
        "difficulty": "intermediate",
        "question": "On the Bloch sphere, the state |ψ⟩ = cos(θ/2)|0⟩ + e^{iφ}sin(θ/2)|1⟩ has what geometry?",
        "correct": "θ is the polar angle from the +Z axis; φ is the azimuthal angle around Z",
        "choices": [
            "θ is the polar angle from the +Z axis; φ is the azimuthal angle around Z",
            "θ is the azimuthal angle; φ is the elevation",
            "θ and φ are both phases; there is no geometric interpretation",
            "θ = 0 always corresponds to the equator",
        ],
        "steps": [
            "The Bloch sphere embeds a qubit as a point on the unit sphere in R³.",
            "θ ∈ [0, π]: θ=0 is the north pole |0⟩, θ=π is the south pole |1⟩.",
            "φ ∈ [0, 2π]: the azimuthal angle. φ=0 gives the +X hemisphere (|+⟩ family).",
        ],
        "concepts": ["Bloch sphere", "qubit geometry", "polar angle"],
    },
    {
        "difficulty": "intermediate",
        "question": "What is the Y eigenstates |+Y⟩ and |−Y⟩ in the computational basis?",
        "correct": "|+Y⟩ = (|0⟩+i|1⟩)/√2,  |−Y⟩ = (|0⟩−i|1⟩)/√2",
        "choices": [
            "|+Y⟩ = (|0⟩+i|1⟩)/√2,  |−Y⟩ = (|0⟩−i|1⟩)/√2",
            "|+Y⟩ = (|0⟩+|1⟩)/√2,  |−Y⟩ = (|0⟩−|1⟩)/√2",
            "|+Y⟩ = |0⟩,  |−Y⟩ = |1⟩",
            "|+Y⟩ = (i|0⟩+|1⟩)/√2,  |−Y⟩ = (i|0⟩−|1⟩)/√2",
        ],
        "steps": [
            "Y eigenstates satisfy Y|±Y⟩ = ±|±Y⟩.",
            "Y = [[0,−i],[i,0]]: solving gives |+Y⟩ = (|0⟩+i|1⟩)/√2 and |−Y⟩ = (|0⟩−i|1⟩)/√2.",
            "These are the +Y and −Y poles on the Bloch sphere (equator, 90° from ±X).",
        ],
        "concepts": ["Y eigenstates", "Pauli operators", "Bloch sphere"],
    },
    # ── Additional beginner ───────────────────────────────────────────────────
    {
        "difficulty": "beginner",
        "question": "What is the bra-ket inner product ⟨0|0⟩?",
        "correct": "1 (a normalised state has unit self-inner-product)",
        "choices": [
            "1 (a normalised state has unit self-inner-product)",
            "0",
            "2",
            "Undefined",
        ],
        "steps": [
            "|0⟩ = [1,0]ᵀ, so ⟨0| = [1,0].",
            "⟨0|0⟩ = [1,0]·[1,0]ᵀ = 1.",
            "All basis states are normalised: ⟨0|0⟩ = ⟨1|1⟩ = 1.",
        ],
        "concepts": ["inner product", "normalisation", "Dirac notation"],
    },
    {
        "difficulty": "beginner",
        "question": "What does H⊗n|0⟩^⊗n produce?",
        "correct": "An equal superposition of all 2ⁿ computational basis states",
        "choices": [
            "An equal superposition of all 2ⁿ computational basis states",
            "The all-zeros state |00…0⟩",
            "A GHZ state",
            "A random basis state",
        ],
        "steps": [
            "H|0⟩ = (|0⟩+|1⟩)/√2 on each qubit independently.",
            "H⊗n|0⟩^⊗n = (1/√2ⁿ) Σ_{x∈{0,1}ⁿ} |x⟩.",
            "All 2ⁿ basis states appear with equal amplitude 1/√2ⁿ.",
        ],
        "concepts": ["tensor product", "Hadamard transform", "superposition"],
    },
    {
        "difficulty": "beginner",
        "question": "What is the |−⟩ state as a column vector?",
        "correct": "[1/√2, −1/√2]ᵀ",
        "choices": [
            "[1/√2, −1/√2]ᵀ",
            "[1/√2, 1/√2]ᵀ",
            "[1, −1]ᵀ",
            "[0, 1]ᵀ",
        ],
        "steps": [
            "|−⟩ = (|0⟩ − |1⟩)/√2.",
            "|0⟩ = [1,0]ᵀ, |1⟩ = [0,1]ᵀ.",
            "|−⟩ = [1/√2, −1/√2]ᵀ.",
        ],
        "concepts": ["|−⟩ state", "column vector", "superposition"],
    },
    # ── Advanced ──────────────────────────────────────────────────────────────
    {
        "difficulty": "advanced",
        "question": "What is the outer product |0⟩⟨1| as a matrix?",
        "correct": "[[0,1],[0,0]] — the raising operator σ₊",
        "choices": [
            "[[0,1],[0,0]] — the raising operator σ₊",
            "[[0,0],[1,0]] — the lowering operator σ₋",
            "[[1,0],[0,0]] — the projector onto |0⟩",
            "[[0,0],[0,1]] — the projector onto |1⟩",
        ],
        "steps": [
            "|0⟩⟨1| is an outer product (rank-1 matrix).",
            "|0⟩ = [1,0]ᵀ, ⟨1| = [0,1] (row vector).",
            "|0⟩⟨1| = [[1],[0]] · [[0,1]] = [[0,1],[0,0]].",
            "This raises |1⟩ to |0⟩: |0⟩⟨1||1⟩ = |0⟩⟨1|1⟩ = |0⟩.",
        ],
        "concepts": ["outer product", "projectors", "raising/lowering operators"],
    },
    {
        "difficulty": "advanced",
        "question": "In the spectral decomposition A = Σᵢ λᵢ |aᵢ⟩⟨aᵢ|, what are the |aᵢ⟩⟨aᵢ| terms?",
        "correct": "Orthogonal projectors onto the eigenspaces of A",
        "choices": [
            "Orthogonal projectors onto the eigenspaces of A",
            "The eigenvalues of A",
            "The matrix elements of A in the computational basis",
            "The Pauli decomposition of A",
        ],
        "steps": [
            "|aᵢ⟩⟨aᵢ| projects onto the eigenspace for eigenvalue λᵢ.",
            "Each projector Πᵢ = |aᵢ⟩⟨aᵢ| satisfies Πᵢ² = Πᵢ and Πᵢ† = Πᵢ.",
            "They are orthogonal: Πᵢ Πⱼ = 0 for i≠j, and Σ Πᵢ = I.",
        ],
        "concepts": ["spectral decomposition", "projectors", "Hermitian operators"],
    },
    {
        "difficulty": "advanced",
        "question": "What does the notation [[n,k,d]] denote in quantum error correction?",
        "correct": "An [[n,k,d]] stabilizer code: n physical qubits, k logical qubits, distance d",
        "choices": [
            "An [[n,k,d]] stabilizer code: n physical qubits, k logical qubits, distance d",
            "A classical [n,k,d] binary linear code",
            "n qubits, k stabilizer generators, d syndrome bits",
            "A code that corrects d errors using n+k qubits",
        ],
        "steps": [
            "[[n,k,d]] is the standard quantum code notation.",
            "n = total physical qubits used.",
            "k = logical qubits encoded (information qubits).",
            "d = code distance: detects d−1 errors, corrects ⌊(d−1)/2⌋ errors.",
        ],
        "concepts": ["quantum error correction", "stabilizer codes", "code distance"],
    },
    {
        "difficulty": "advanced",
        "question": "Any 2×2 Hermitian matrix M can be written as M = aI + bX + cY + dZ. What is this expansion called?",
        "correct": "Pauli decomposition (expansion in the Pauli basis)",
        "choices": [
            "Pauli decomposition (expansion in the Pauli basis)",
            "Schmidt decomposition",
            "Bloch vector representation",
            "Jordan-Wigner transformation",
        ],
        "steps": [
            "{I, X, Y, Z} form an orthonormal basis for 2×2 Hermitian matrices under Tr(AB†)/2.",
            "Any H = (Tr(H)/2)I + (Tr(HX)/2)X + (Tr(HY)/2)Y + (Tr(HZ)/2)Z.",
            "This extends to n qubits: any operator is a sum of Pauli strings with coefficients Tr(H·Pᵢ)/2ⁿ.",
        ],
        "concepts": ["Pauli decomposition", "operator basis", "Hermitian operators"],
    },
    {
        "difficulty": "advanced",
        "question": "The von Neumann entropy S(ρ) = −Tr(ρ log ρ). What is S(ρ) for a pure state?",
        "correct": "S = 0  (pure states have zero entropy)",
        "choices": [
            "S = 0  (pure states have zero entropy)",
            "S = 1  (maximum entropy)",
            "S = log 2  (one bit of entropy)",
            "S is undefined for pure states",
        ],
        "steps": [
            "A pure state ρ = |ψ⟩⟨ψ| has eigenvalues {1, 0, 0, …}.",
            "S(ρ) = −Σᵢ λᵢ log λᵢ = −1·log(1) − 0·log(0) = 0.",
            "Maximum entropy (fully mixed state) gives S = log d for d-dimensional system.",
        ],
        "concepts": ["von Neumann entropy", "pure states", "density matrix"],
    },
    {
        "difficulty": "advanced",
        "question": "What is the density matrix ρ for the maximally mixed state of a single qubit?",
        "correct": "ρ = I/2 = [[1/2, 0], [0, 1/2]]",
        "choices": [
            "ρ = I/2 = [[1/2, 0], [0, 1/2]]",
            "ρ = |0⟩⟨0|",
            "ρ = |+⟩⟨+|",
            "ρ = [[0, 1], [1, 0]]/2",
        ],
        "steps": [
            "The maximally mixed state has equal probability 1/2 for any measurement outcome.",
            "ρ = (1/2)|0⟩⟨0| + (1/2)|1⟩⟨1| = I/2.",
            "In the Bloch picture, this is the origin — no preferred direction.",
        ],
        "concepts": ["density matrix", "maximally mixed state", "Bloch sphere"],
    },
    {
        "difficulty": "advanced",
        "question": "In the stabilizer formalism, the stabilizer of |+⟩ = (|0⟩+|1⟩)/√2 is:",
        "correct": "+X  (X|+⟩ = |+⟩)",
        "choices": [
            "+X  (X|+⟩ = |+⟩)",
            "+Z  (Z|+⟩ = |+⟩)",
            "+Y",
            "−Z",
        ],
        "steps": [
            "X|+⟩ = X(|0⟩+|1⟩)/√2 = (|1⟩+|0⟩)/√2 = |+⟩.  ✓",
            "Z|+⟩ = (|0⟩−|1⟩)/√2 = |−⟩ ≠ |+⟩.  ✗",
            "|+⟩ is the +1 eigenstate of X — so X is its stabilizer.",
        ],
        "concepts": ["stabilizer formalism", "Pauli eigenstates", "X eigenstates"],
    },
]


def generate(difficulty: str) -> Problem:
    pool = [(i, q) for i, q in enumerate(NOTATION_QUESTIONS) if q["difficulty"] == difficulty]
    if not pool:
        pool = list(enumerate(NOTATION_QUESTIONS))
    idx, q = random.choice(pool)

    choices = q["choices"][:]
    correct_str = q["correct"]
    random.shuffle(choices)
    correct_idx = choices.index(correct_str)

    return Problem(
        category=ProblemCategory.NOTATION_READING,
        difficulty=difficulty,
        question_text=q["question"],
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=None,
        state_str=None,
        solution_steps=q["steps"],
        key_concepts=q["concepts"],
        problem_id=f"notation:{idx:02d}",   # static pool -> stable id
    )

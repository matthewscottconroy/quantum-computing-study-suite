"""hamiltonians.py -- milestone 1: the H2 Hamiltonian as data.

The table below is the 2-qubit *electronic* H2 Hamiltonian in the STO-3G
basis, as five Pauli coefficients plus the nuclear-repulsion constant, for 17
bond distances spanning 0.30-2.50 angstrom.

    H_el(d) = II*g0 + IZ*g1 - ZI*g1 + ZZ*g3 + XX*g4
    E_total(d) = min eig H_el(d) + e_nuc(d)

It was produced by ``sto3g.py`` (run it as a script to regenerate) rather than
copied out of a paper, so every number is reproducible and the derivation is
in the open.  ``test_solution.py::test_table_matches_ab_initio`` re-runs the
generator and asserts the table is unchanged.

Cross-check against the literature anchor quoted in the spec (the standard
Qiskit 0.735 angstrom Hamiltonian, itself derived from a PySCF STO-3G run):
this table agrees to 8.1e-9 hartree -- five millionths of a milli-hartree,
i.e. 200000x tighter than chemical accuracy.  The residual is basis-set
constant precision, not physics.
"""

from __future__ import annotations

import numpy as np
from qiskit.quantum_info import SparsePauliOp

# The literature anchor from the spec, kept for the cross-check test only.
ANCHOR_0735 = {
    "II": -1.052373245772859,
    "IZ": 0.39793742484318045,
    "ZI": -0.39793742484318045,
    "ZZ": -0.01128010425623538,
    "XX": 0.18093119978423156,
}

# d(angstrom) -> (II, IZ, ZZ, XX, e_nuc).  ZI is always -IZ (see sto3g.py).
TABLE: dict[float, tuple[float, float, float, float, float]] = {
    0.300: (-0.7537419738699191, 0.8086488980766431, -0.013287977078207336, 0.16081851883596235, 1.7639240363433333),
    0.400: (-0.8625795492807893, 0.6888194201504269, -0.012913969349398313, 0.16451542355694457, 1.3229430272574998),
    0.500: (-0.9477078909001637, 0.5830796182085008, -0.012516431621820479, 0.168870227160001, 1.058354421806),
    0.600: (-1.0071270879230358, 0.49401378101386517, -0.012064389760916727, 0.17373064317255554, 0.8819620181716666),
    0.700: (-1.043912530446865, 0.42045567549305357, -0.01150740223712865, 0.17900057546328024, 0.7559674441471428),
    0.735: (-1.0523732538186334, 0.39793742091254314, -0.011280104316990891, 0.18093119918149508, 0.7199689944258503),
    0.800: (-1.0632128041719537, 0.3599594211180591, -0.010809735016291677, 0.18462678295016755, 0.6614715136287499),
    0.900: (-1.0702832749931321, 0.3097872768131701, -0.009969108370496138, 0.19057169316133557, 0.5879746787811111),
    1.000: (-1.0692434954840162, 0.2675286477016263, -0.009014930101938323, 0.19679058290932827, 0.529177210903),
    1.100: (-1.062812491980968, 0.23139587526456806, -0.007995175095105389, 0.20322222607815177, 0.48107019172999993),
    1.200: (-1.0526707284911625, 0.20018957517152247, -0.006962162449051568, 0.20979146812352367, 0.4409810090858333),
    1.300: (-1.0399165920377382, 0.1731078515878505, -0.005962285645683685, 0.2164174591763562, 0.40705939300230765),
    1.500: (-1.009644697289736, 0.12910131182227216, -0.00418895824372123, 0.229535935730663, 0.3527848072686666),
    1.700: (-0.9767372390031048, 0.09584458579605479, -0.002808070584156608, 0.24207283831406717, 0.31128071229588233),
    2.000: (-0.9285563479344376, 0.06062800813062014, -0.0014311038845634116, 0.2591384748398962, 0.2645886054515),
    2.250: (-0.8923856712837683, 0.04086723381361981, -0.0007614396744182739, 0.27151164724040733, 0.23518987151244442),
    2.500: (-0.8607225068721522, 0.027134698805235252, -0.0003774199171373005, 0.28221004609698785, 0.2116708843612),
}

DISTANCES: tuple[float, ...] = tuple(sorted(TABLE))


def _row(d: float) -> tuple[float, float, float, float, float]:
    """Exact table lookup, tolerant of float noise in the key."""
    for key, row in TABLE.items():
        if abs(key - d) < 1e-9:
            return row
    raise KeyError(
        f"no tabulated Hamiltonian at d={d} angstrom; "
        f"available: {', '.join(f'{k:.3f}' for k in DISTANCES)} "
        f"(or call sto3g.pauli_coefficients(d) to compute a new one)"
    )


def hamiltonian(d: float) -> SparsePauliOp:
    """The 2-qubit electronic H2 Hamiltonian at bond distance ``d`` angstrom."""
    g0, g1, g3, g4, _ = _row(d)
    return SparsePauliOp.from_list([
        ("II", g0), ("IZ", g1), ("ZI", -g1), ("ZZ", g3), ("XX", g4),
    ])


def nuclear_repulsion(d: float) -> float:
    """Nuclear-repulsion constant 1/R in hartree (R in bohr)."""
    return _row(d)[4]


def exact_energy(d: float) -> float:
    """Exact *electronic* ground energy: min eig of the 4x4 Hamiltonian.

    TRAP: this is the quantity the VQE minimises and the quantity the spec's
    -1.857275 anchor refers to.  It falls monotonically as the nuclei
    approach; the *minimum near 0.74 angstrom* only appears in
    ``total_energy`` once nuclear repulsion is added back.
    """
    return float(np.linalg.eigvalsh(hamiltonian(d).to_matrix()).real.min())


def total_energy(d: float) -> float:
    """Born-Oppenheimer total energy: electronic + nuclear repulsion."""
    return exact_energy(d) + nuclear_repulsion(d)


def exact_ground_state(d: float) -> np.ndarray:
    """Exact ground eigenvector (little-endian Qiskit ordering)."""
    vals, vecs = np.linalg.eigh(hamiltonian(d).to_matrix())
    return np.asarray(vecs[:, int(np.argmin(vals.real))]).ravel()


def equilibrium_distance(energies: dict[float, float] | None = None) -> float:
    """Bond distance minimising a {d: total energy} curve (default: exact)."""
    if energies is None:
        energies = {d: total_energy(d) for d in DISTANCES}
    return min(energies, key=lambda d: energies[d])


CHEMICAL_ACCURACY = 1.6e-3  # hartree

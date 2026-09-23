"""sto3g.py -- a 120-line ab-initio engine for H2 in the STO-3G basis.

Why this file exists
--------------------
Milestone 1 of the spec says "without a chemistry package in the venv,
hard-code a table of coefficients from the literature".  That is the right
*minimum*, but a table of magic numbers teaches nothing about where the
Hamiltonian comes from, and it cannot be regenerated at a distance the table
does not contain.

H2 in a minimal basis is small enough that the integrals are analytic: every
basis function is a contraction of three s-type Gaussians, and the overlap,
kinetic, nuclear-attraction and two-electron integrals over s Gaussians all
have closed forms (Szabo & Ostlund, *Modern Quantum Chemistry*, Appendix A).
So this module computes the table instead of quoting it, and
``hamiltonians.py`` freezes the result into a literal table so the rest of the
project needs neither scipy nor this file at import time.

The whole engine is ~40 lines of physics; the rest is bookkeeping.

Formulas (unnormalised primitives g_a(r) = exp(-a |r - A|^2), p = a + b):

    S_ab   = (pi/p)^{3/2} K_ab
    T_ab   = (a b / p) (3 - 2 (a b / p) |A-B|^2) (pi/p)^{3/2} K_ab
    V_ab^C = -2 pi Z_C / p * K_ab * F0(p |P - C|^2)
    (ab|cd) = 2 pi^{5/2} / (p q sqrt(p+q)) * K_ab K_cd * F0(pq/(p+q) |P-Q|^2)

with K_ab = exp(-(a b / p) |A-B|^2), P the Gaussian-product centre, and the
Boys function F0(t) = sqrt(pi/4t) erf(sqrt(t)), F0(0) = 1.
"""

from __future__ import annotations

import numpy as np
from scipy.special import erf

# CODATA 2018 bohr radius, in angstrom.  The table in hamiltonians.py is
# indexed by bond distance in ANGSTROM because that is what the spec uses.
BOHR_ANGSTROM = 0.529177210903

# STO-3G contraction for hydrogen (zeta = 1.24), as published in the EMSL /
# Basis Set Exchange library.
STO3G_ALPHA = np.array([3.425250914, 0.6239137298, 0.1688554040])
STO3G_COEF = np.array([0.1543289673, 0.5353281423, 0.4446345422])
# Fold the primitive normalisation (2a/pi)^{3/4} into the contraction
# coefficients once, so the integral loops below deal with bare Gaussians.
_D = STO3G_COEF * (2.0 * STO3G_ALPHA / np.pi) ** 0.75


def boys_f0(t: np.ndarray | float) -> np.ndarray:
    """Boys function F0(t), numerically safe at t -> 0."""
    t = np.asarray(t, dtype=float)
    small = t < 1e-12
    safe = np.where(small, 1.0, t)
    return np.where(small, 1.0 - t / 3.0,
                    0.5 * np.sqrt(np.pi / safe) * erf(np.sqrt(safe)))


def ao_integrals(r_bohr: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Atomic-orbital integrals for H2 with the nuclei at 0 and ``r_bohr``.

    Returns ``(S, Hcore, eri)`` where ``eri`` is in *chemist* notation
    ``(pq|rs) = \\int p(1) q(1) (1/r12) r(2) s(2)``.
    """
    centre = np.array([0.0, r_bohr])
    n = 2
    S = np.zeros((n, n))
    Hcore = np.zeros((n, n))

    for A in range(n):
        for B in range(n):
            rab2 = (centre[A] - centre[B]) ** 2
            for a, da in zip(STO3G_ALPHA, _D):
                for b, db in zip(STO3G_ALPHA, _D):
                    p = a + b
                    mu = a * b / p
                    k = np.exp(-mu * rab2)
                    w = da * db
                    S[A, B] += w * (np.pi / p) ** 1.5 * k
                    Hcore[A, B] += w * mu * (3 - 2 * mu * rab2) * (np.pi / p) ** 1.5 * k
                    P = (a * centre[A] + b * centre[B]) / p
                    for C in range(n):  # Z = 1 for both protons
                        Hcore[A, B] += w * (-2.0 * np.pi / p) * k * float(
                            boys_f0(p * (P - centre[C]) ** 2))

    eri = np.zeros((n, n, n, n))
    for A in range(n):
        for B in range(n):
            rab2 = (centre[A] - centre[B]) ** 2
            for C in range(n):
                for D in range(n):
                    rcd2 = (centre[C] - centre[D]) ** 2
                    acc = 0.0
                    for a, da in zip(STO3G_ALPHA, _D):
                        for b, db in zip(STO3G_ALPHA, _D):
                            p = a + b
                            P = (a * centre[A] + b * centre[B]) / p
                            kab = np.exp(-a * b / p * rab2)
                            for c, dc in zip(STO3G_ALPHA, _D):
                                for d, dd in zip(STO3G_ALPHA, _D):
                                    q = c + d
                                    Q = (c * centre[C] + d * centre[D]) / q
                                    kcd = np.exp(-c * d / q * rcd2)
                                    acc += (da * db * dc * dd
                                            * 2 * np.pi ** 2.5 / (p * q * np.sqrt(p + q))
                                            * kab * kcd
                                            * float(boys_f0(p * q / (p + q) * (P - Q) ** 2)))
                    eri[A, B, C, D] = acc
    return S, Hcore, eri


def mo_quantities(d_angstrom: float) -> dict[str, float]:
    """Molecular-orbital integrals for H2 at bond distance ``d_angstrom``.

    For a homonuclear diatomic in a minimal basis the RHF orbitals are fixed
    by symmetry -- no SCF iteration is needed:

        sigma_g = (chi_A + chi_B) / sqrt(2(1 + S)),
        sigma_u = (chi_A - chi_B) / sqrt(2(1 - S)).

    That is the single most useful simplification in this project: it removes
    the only part of a quantum-chemistry stack that could disagree with a
    reference implementation.
    """
    r = d_angstrom / BOHR_ANGSTROM
    S, Hcore, eri = ao_integrals(r)
    s = S[0, 1]
    C = np.stack([np.array([1.0, 1.0]) / np.sqrt(2 * (1 + s)),
                  np.array([1.0, -1.0]) / np.sqrt(2 * (1 - s))], axis=1)
    h = C.T @ Hcore @ C
    g = np.einsum("pi,qj,rk,sl,pqrs->ijkl", C, C, C, C, eri, optimize=True)
    return {
        "h_gg": float(h[0, 0]),
        "h_uu": float(h[1, 1]),
        "J_gg": float(g[0, 0, 0, 0]),   # (gg|gg)
        "J_uu": float(g[1, 1, 1, 1]),   # (uu|uu)
        "J_gu": float(g[0, 0, 1, 1]),   # (gg|uu)  Coulomb
        "K_gu": float(g[0, 1, 0, 1]),   # (gu|gu)  exchange
        "e_nuc": float(1.0 / r),
        "overlap": float(s),
    }


def pauli_coefficients(d_angstrom: float) -> dict[str, float]:
    """The five coefficients of the 2-qubit *electronic* H2 Hamiltonian.

    Derivation (this is the heart of milestone 1 -- see SOLUTION.md):

    In the two-spatial-orbital active space the singlet, Sz = 0 sector has
    three configurations; g/u symmetry blocks the closed-shell pair
    {|sigma_g^2>, |sigma_u^2>} away from the open-shell one.  Writing

        a = E(sigma_g^2)   = 2 h_gg + (gg|gg)
        b = E(sigma_u^2)   = 2 h_uu + (uu|uu)
        c = E(sigma_g sigma_u) = h_gg + h_uu + (gg|uu)
        K = (gu|gu)

    the 2-qubit Hamiltonian  g0 II + g1 IZ + g2 ZI + g3 ZZ + g4 XX  has to
    have diagonal (c, a, b, c) on (|00>, |01>, |10>, |11>) and off-diagonal K.
    Solving the four linear equations gives g2 = -g1 and

        g1 = (b - a)/4,  g0 = (c + (a+b)/2)/2,  g3 = (c - (a+b)/2)/2,  g4 = K.

    |01> is the Hartree-Fock reference (sigma_g doubly occupied) and |10> is
    the double excitation; XX is what mixes them.
    """
    q = mo_quantities(d_angstrom)
    a = 2 * q["h_gg"] + q["J_gg"]
    b = 2 * q["h_uu"] + q["J_uu"]
    c = q["h_gg"] + q["h_uu"] + q["J_gu"]
    mean = 0.5 * (a + b)
    return {
        "II": 0.5 * (c + mean),
        "IZ": 0.25 * (b - a),
        "ZI": -0.25 * (b - a),
        "ZZ": 0.5 * (c - mean),
        "XX": q["K_gu"],
        "e_nuc": q["e_nuc"],
    }


if __name__ == "__main__":  # pragma: no cover - table generator
    # Regenerates the literal table pasted into hamiltonians.py.
    from hamiltonians import DISTANCES

    print("# d(A)      II                  IZ                  ZZ"
          "                  XX                  e_nuc")
    for d in DISTANCES:
        c = pauli_coefficients(d)
        print(f"    {d:.3f}: ({c['II']!r}, {c['IZ']!r}, "
              f"{c['ZZ']!r}, {c['XX']!r}, {c['e_nuc']!r}),")

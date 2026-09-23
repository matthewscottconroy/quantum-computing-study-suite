"""vqe.py -- milestone 3: the VQE loop, with a hand-written parameter-shift gradient.

Everything here is noiseless-statevector by default; the noisy (fake-backend)
path lives in ``noisy.py`` so that the pure-simulation tests never import
qiskit-ibm-runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp
from scipy.optimize import minimize

from ansatz import Ansatz


@dataclass
class VQEResult:
    energy: float
    x: np.ndarray
    nfev: int          # energy evaluations
    ngev: int = 0      # gradient evaluations
    n_circuits: int = 0  # circuits actually executed (the honest cost)
    method: str = ""
    history: list[float] = field(default_factory=list)


class EnergyFunction:
    """<psi(theta)| H |psi(theta)> with a call counter.

    ``precision`` > 0 makes ``StatevectorEstimator`` add Gaussian noise of
    that standard deviation to each expectation value, which is how the
    milestone-5 "sampling" error term is produced without leaving the
    statevector simulator.  precision = 0 is exact.
    """

    def __init__(self, ansatz: Ansatz, hamiltonian: SparsePauliOp,
                 precision: float = 0.0, seed: int | None = None) -> None:
        self.ansatz = ansatz
        self.hamiltonian = hamiltonian
        self.precision = precision
        self.estimator = StatevectorEstimator(default_precision=precision, seed=seed)
        self.nfev = 0

    def __call__(self, x) -> float:
        x = np.atleast_1d(np.asarray(x, dtype=float))
        self.nfev += 1
        job = self.estimator.run([(self.ansatz.circuit, self.hamiltonian, x)])
        return float(job.result()[0].data.evs)

    def batch(self, xs: np.ndarray) -> np.ndarray:
        """Evaluate many parameter vectors in one estimator call."""
        xs = np.atleast_2d(np.asarray(xs, dtype=float))
        self.nfev += len(xs)
        job = self.estimator.run([(self.ansatz.circuit, self.hamiltonian, xs)])
        return np.asarray(job.result()[0].data.evs, dtype=float).ravel()


def parameter_shift_gradient(energy: EnergyFunction, x) -> np.ndarray:
    """Exact analytic gradient by the two-term parameter-shift rule.

        dE/dtheta_i = [ E(theta_i + pi/2) - E(theta_i - pi/2) ] / 2

    Valid because every parameter in every ansatz here enters through a single
    Pauli rotation exp(-i theta P / 2) with P^2 = I, so the eigenvalues of the
    generator are +-1/2.  This is *exact*, not an approximation -- which is
    the whole point, and the reason it beats finite differences under shot
    noise.  Cost: 2 circuits per parameter, evaluated here in one batch.
    """
    x = np.atleast_1d(np.asarray(x, dtype=float))
    n = x.size
    shifts = np.repeat(x[None, :], 2 * n, axis=0)
    idx = np.arange(n)
    shifts[idx, idx] += np.pi / 2
    shifts[n + idx, idx] -= np.pi / 2
    vals = energy.batch(shifts)
    return 0.5 * (vals[:n] - vals[n:])


def finite_difference_gradient(energy: EnergyFunction, x, eps: float = 1e-6) -> np.ndarray:
    """Central differences -- the thing parameter shift is compared against."""
    x = np.atleast_1d(np.asarray(x, dtype=float))
    out = np.empty(x.size)
    for i in range(x.size):
        xp, xm = x.copy(), x.copy()
        xp[i] += eps
        xm[i] -= eps
        out[i] = (energy(xp) - energy(xm)) / (2 * eps)
    return out


def run_cobyla(ansatz: Ansatz, hamiltonian: SparsePauliOp, *, x0=None,
               maxiter: int = 400, precision: float = 0.0,
               seed: int | None = None) -> VQEResult:
    """Gradient-free reference optimiser."""
    energy = EnergyFunction(ansatz, hamiltonian, precision=precision, seed=seed)
    history: list[float] = []

    def wrapped(x):
        e = energy(x)
        history.append(e)
        return e

    x0 = ansatz.x0 if x0 is None else np.asarray(x0, dtype=float)
    res = minimize(wrapped, x0, method="COBYLA",
                   options={"maxiter": maxiter, "tol": 1e-10})
    return VQEResult(float(res.fun), np.atleast_1d(res.x), energy.nfev,
                     0, energy.nfev, "COBYLA", history)


def run_gradient(ansatz: Ansatz, hamiltonian: SparsePauliOp, *, x0=None,
                 maxiter: int = 200, precision: float = 0.0,
                 seed: int | None = None, method: str = "L-BFGS-B") -> VQEResult:
    """Gradient optimiser fed by the parameter-shift rule (never by SciPy's
    own finite differences -- ``jac`` is supplied explicitly)."""
    energy = EnergyFunction(ansatz, hamiltonian, precision=precision, seed=seed)
    history: list[float] = []
    ngev = 0

    def fun(x):
        e = energy(x)
        history.append(e)
        return e

    def jac(x):
        nonlocal ngev
        ngev += 1
        return parameter_shift_gradient(energy, x)

    x0 = ansatz.x0 if x0 is None else np.asarray(x0, dtype=float)
    res = minimize(fun, x0, jac=jac, method=method,
                   options={"maxiter": maxiter, "gtol": 1e-10})
    n_energy_calls = len(history)
    return VQEResult(float(res.fun), np.atleast_1d(res.x), n_energy_calls,
                     ngev, energy.nfev, f"parameter-shift/{method}", history)


def run_plain_gradient_descent(ansatz: Ansatz, hamiltonian: SparsePauliOp, *,
                               x0=None, lr: float = 0.3, maxiter: int = 200,
                               tol: float = 1e-10) -> VQEResult:
    """Vanilla steepest descent -- the pedagogical version of the above."""
    energy = EnergyFunction(ansatz, hamiltonian)
    x = np.atleast_1d(np.array(ansatz.x0 if x0 is None else x0, dtype=float))
    history = []
    for _ in range(maxiter):
        e = energy(x)
        history.append(e)
        g = parameter_shift_gradient(energy, x)
        if np.linalg.norm(g) < tol:
            break
        x = x - lr * g
    return VQEResult(float(energy(x)), x, len(history), len(history),
                     energy.nfev, "plain gradient descent", history)


def grid_minimum(ansatz: Ansatz, hamiltonian: SparsePauliOp, *,
                 points: int = 161, polish: bool = True) -> tuple[float, np.ndarray]:
    """Best energy the ansatz can reach: the *expressibility* floor.

    For <= 2 parameters this is a genuine grid over [0, 2pi]^n (the criterion
    as written).  For the 8-parameter hardware-efficient ansatz a grid is
    hopeless -- 161^8 points -- so a seeded multi-start local search is used
    instead and the substitution is reported rather than hidden.
    """
    n = ansatz.num_parameters
    energy = EnergyFunction(ansatz, hamiltonian)
    if n <= 2:
        axis = np.linspace(0.0, 2 * np.pi, points)
        if n == 1:
            pts = axis[:, None]
        else:
            A, B = np.meshgrid(axis, axis, indexing="ij")
            pts = np.stack([A.ravel(), B.ravel()], axis=1)
        vals = energy.batch(pts)
        best = int(np.argmin(vals))
        e0, x0 = float(vals[best]), pts[best]
    else:
        rng = np.random.default_rng(20240917)
        starts = rng.uniform(-np.pi, np.pi, size=(24, n))
        e0, x0 = np.inf, starts[0]
        for s in starts:
            r = minimize(energy, s, jac=lambda z: parameter_shift_gradient(energy, z),
                         method="L-BFGS-B", options={"maxiter": 500})
            if r.fun < e0:
                e0, x0 = float(r.fun), np.atleast_1d(r.x)
    if polish:
        r = minimize(energy, x0, jac=lambda z: parameter_shift_gradient(energy, z),
                     method="L-BFGS-B", options={"maxiter": 500, "gtol": 1e-14})
        if r.fun < e0:
            e0, x0 = float(r.fun), np.atleast_1d(r.x)
    return e0, np.asarray(x0, dtype=float)

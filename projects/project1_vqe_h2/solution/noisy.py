"""noisy.py -- milestone 4: the same VQE against a fake backend's noise model.

This is the only module that imports qiskit-ibm-runtime.  It runs entirely
locally: ``EstimatorV2(mode=FakeManilaV2())`` is the runtime's *local testing
mode*, which builds an Aer noise model from the fake backend's calibration
snapshot.  No account, no API key, no network.

The lab-5 gotchas that bite here, in the order they bite:

1. The observable must be transpiled *with* the circuit.  ``pass_manager.run``
   relabels and pads the circuit to the backend's 5 qubits; a 2-qubit
   ``SparsePauliOp`` no longer matches it.  ``H.apply_layout(isa.layout)``
   rewrites the observable onto the physical qubits.  Skipping this raises
   a shape error at best and silently measures the wrong qubits at worst.
2. Transpile *once*, outside the optimisation loop.  The ansatz is fixed; only
   the observable's coefficients change with bond distance.
3. Guard the entry point with ``if __name__ == "__main__":`` -- Aer's
   parallel execution uses forkserver on Python 3.14 and re-imports the module
   in the child process.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
from scipy.optimize import minimize

from ansatz import Ansatz


@dataclass
class NoisyResult:
    energy: float
    x: np.ndarray
    nfev: int
    stderr: float     # the estimator's own shot-noise standard error at the optimum


class NoisyEnergy:
    """Shot-based, noise-model-based <H> on a fake backend."""

    def __init__(self, ansatz: Ansatz, backend=None, *, shots: int = 2048,
                 seed_transpiler: int = 1, seed_simulator: int = 11,
                 optimization_level: int = 3) -> None:
        self.backend = backend if backend is not None else FakeManilaV2()
        self.pm = generate_preset_pass_manager(
            optimization_level=optimization_level, backend=self.backend,
            seed_transpiler=seed_transpiler)
        self.isa = self.pm.run(ansatz.circuit)          # gotcha 2: transpile once
        self.estimator = EstimatorV2(mode=self.backend)
        self.estimator.options.default_shots = shots
        self.estimator.options.simulator.seed_simulator = seed_simulator
        self.nfev = 0
        self.last_stderr = 0.0

    def __call__(self, x, hamiltonian) -> float:
        obs = hamiltonian.apply_layout(self.isa.layout)  # gotcha 1
        self.nfev += 1
        res = self.estimator.run([(self.isa, obs, np.atleast_1d(x))]).result()[0]
        self.last_stderr = float(np.asarray(res.data.stds).ravel()[0])
        return float(np.asarray(res.data.evs).ravel()[0])


def run_noisy_vqe(ansatz: Ansatz, hamiltonian, *, shots: int = 2048,
                  seed_simulator: int = 11, maxiter: int = 40,
                  rhobeg: float = 0.4, backend=None) -> NoisyResult:
    """COBYLA against the noisy estimator.

    Gradient methods are deliberately *not* used here: with 2048 shots the
    parameter-shift gradient has a standard error comparable to the gradient
    itself near the optimum, and L-BFGS's line search chases the noise.
    Gradient-free COBYLA is the standard NISQ choice for exactly this reason.
    """
    energy = NoisyEnergy(ansatz, backend=backend, shots=shots,
                         seed_simulator=seed_simulator)
    res = minimize(lambda x: energy(x, hamiltonian), ansatz.x0,
                   method="COBYLA", options={"maxiter": maxiter, "rhobeg": rhobeg})
    return NoisyResult(float(res.fun), np.atleast_1d(res.x), energy.nfev,
                       energy.last_stderr)

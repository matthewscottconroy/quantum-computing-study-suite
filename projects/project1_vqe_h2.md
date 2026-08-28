# Project 1 — VQE Dissociation Curve for H₂

**Deliverable:** a program that computes the H₂ ground-state energy across bond
distances (the dissociation curve) with a variational quantum eigensolver you
assembled yourself — Hamiltonian, ansatz, optimizer, and error analysis — and a
report showing where you achieve **chemical accuracy (1.6 mHa = 0.0016
hartree)** against exact diagonalization.

**Background:** VQE (Peruzzo et al., 2014) finds ground states by minimizing
⟨ψ(θ)|H|ψ(θ)⟩ over a parameterized circuit. H₂ in a minimal basis reduces to a
2-qubit (even 1-qubit, after symmetry reduction) problem — small enough to
verify everything exactly, rich enough to exercise the whole pipeline. Read
[docs/06_variational_quantum_algorithms/01_vqe_fundamentals.md](../docs/06_variational_quantum_algorithms/01_vqe_fundamentals.md),
[02_ansatz_design.md](../docs/06_variational_quantum_algorithms/02_ansatz_design.md), and
[03_parameter_shift_gradient.md](../docs/06_variational_quantum_algorithms/03_parameter_shift_gradient.md)
first; [lab 5](../labs/lab5_full_workflow.md) is the single-point hardware
version of this project.

---

## Milestones

### M1 — Hamiltonian as data

Build `hamiltonian(d) -> SparsePauliOp` returning the 2-qubit H₂ Hamiltonian
at bond distance `d` for at least 8 distances in 0.3–2.5 Å. Without a chemistry
package in the venv, hard-code a table of coefficients from the literature
(the O'Malley et al. 2016 scalable-VQE paper tabulates the g₀…g₄ coefficients
of `g0·II + g1·ZI + g2·IZ + g3·ZZ + g4·XX (+ g5·YY)` vs. bond length — cite
whatever source you use in your NOTES.md). The verified 0.735 Å point to anchor
your table (executed against the venv; exact ground energy −1.857275 Ha):

```python
from qiskit.quantum_info import SparsePauliOp
H_0735 = SparsePauliOp.from_list([
    ("II", -1.052373245772859), ("IZ", 0.39793742484318045),
    ("ZI", -0.39793742484318045), ("ZZ", -0.01128010425623538),
    ("XX", 0.18093119978423156),
])
```

**Acceptance criteria:**
- [ ] `hamiltonian(0.735)` reproduces the anchor coefficients.
- [ ] `exact_energy(d) = min(np.linalg.eigvalsh(H.to_matrix()))` runs for all
      distances and produces a smooth curve with a minimum near 0.74 Å.
- [ ] A test asserts `exact_energy(0.735) == pytest.approx(-1.857275, abs=1e-5)`.

### M2 — Ansatz zoo

Implement at least three ansätze behind one interface: (a) hardware-efficient
(`efficient_su2` — note: lowercase *function* in Qiskit 2.x,
`qiskit.circuit.library`), (b) a hand-built 2-parameter circuit exploiting the
real-amplitudes structure of this H, (c) a UCC-inspired single-excitation
ansatz (one parameter: `exp(-iθ Y⊗X /2)`-style — derive it from
[docs/06.../02_ansatz_design.md](../docs/06_variational_quantum_algorithms/02_ansatz_design.md)).

**Acceptance criteria:**
- [ ] Each ansatz reports its parameter count; (b) and (c) have ≤ 2 parameters.
- [ ] A statevector scan shows each ansatz *can express* the true ground state
      at 0.735 Å (min over a parameter grid within 1 mHa of exact).
- [ ] A test verifies ansatz (c) applied to |01⟩ (Hartree–Fock) with θ=0
      returns |01⟩.

### M3 — The VQE loop

Wire ansatz + `StatevectorEstimator` (noiseless, `qiskit.primitives`) +
`scipy.optimize.minimize`. Support COBYLA and at least one gradient method
using the **parameter-shift rule** you implement yourself (not finite
differences).

**Acceptance criteria:**
- [ ] Noiseless VQE at 0.735 Å reaches < 0.1 mHa error for every ansatz.
- [ ] Your parameter-shift gradient matches finite differences to 1e-6 on a
      random parameter point (test).
- [ ] Evaluation-count comparison COBYLA vs gradient descent is recorded in
      NOTES.md.

### M4 — Dissociation curve + chemical accuracy

Run the full curve, noiseless. Then rerun with shot noise
(`EstimatorV2(mode=FakeManilaV2())`, the [lab 5](../labs/lab5_full_workflow.md)
pattern — verified: noisy single-point VQE lands ~20–60 mHa high).

**Acceptance criteria:**
- [ ] Plot: exact curve, noiseless-VQE points, noisy-VQE points with error
      bars, on one figure; equilibrium distance from your curve within 0.05 Å
      of the exact curve's minimum.
- [ ] Noiseless VQE is within chemical accuracy (1.6 mHa) at **every**
      distance; the plot marks the chemical-accuracy band.
- [ ] The noisy points quantify the noise penalty (mHa vs distance) in a table.

### M5 — Error analysis & write-up

Where does the error come from? Split it: expressibility (M2 grid-min vs
exact), optimization (converged vs grid-min), sampling (precision setting),
hardware noise (fake backend vs noiseless).

**Acceptance criteria:**
- [ ] A stacked/segmented error-budget chart or table at three distances
      (short, equilibrium, stretched).
- [ ] One paragraph explaining why the stretched geometry is harder (hint:
      the ground state becomes strongly entangled — check the Schmidt
      coefficients, [docs/01.../03_tensor_products...](../docs/01_mathematical_foundations/03_tensor_products_and_multipartite_systems.md)).

---

## Starter scaffolding hints

- Layout: `p1/hamiltonians.py`, `p1/ansatz.py`, `p1/vqe.py`, `p1/run_curve.py`,
  `p1/test_*.py`.
- `SparsePauliOp.to_matrix()` + `np.linalg.eigvalsh` is your exact oracle —
  wrap it once, use it everywhere.
- For noisy runs remember the lab-5 gotchas: transpile with
  `generate_preset_pass_manager`, then `H.apply_layout(isa.layout)`, and guard
  the entry point with `if __name__ == "__main__":` (Python 3.14 forkserver).
- Seed everything (`np.random.default_rng(seed)`); acceptance criteria are
  unreproducible otherwise.

## Stretch goals

- Add the missing `YY` term treatment for a bond-distance-dependent 6-term
  Hamiltonian and show it changes nothing for this symmetry sector — explain why.
- Zero-noise extrapolation on the noisy curve: rerun with gate-folded circuits
  (×1, ×3), extrapolate, and show recovered accuracy
  ([docs/06.../06_noise_and_error_mitigation.md](../docs/06_variational_quantum_algorithms/06_noise_and_error_mitigation.md)).
- Barren-plateau probe: extend `efficient_su2` reps to 1–8 and plot gradient
  variance at random points ([docs/06.../05_barren_plateaus.md](../docs/06_variational_quantum_algorithms/05_barren_plateaus.md)).
- Run the equilibrium point on real hardware via lab 5 checkpoint 4 and add it
  to your curve figure.

## References

- [docs/06_variational_quantum_algorithms/01_vqe_fundamentals.md](../docs/06_variational_quantum_algorithms/01_vqe_fundamentals.md) — the algorithm
- [docs/06_variational_quantum_algorithms/02_ansatz_design.md](../docs/06_variational_quantum_algorithms/02_ansatz_design.md) — M2
- [docs/06_variational_quantum_algorithms/03_parameter_shift_gradient.md](../docs/06_variational_quantum_algorithms/03_parameter_shift_gradient.md) — M3
- [docs/06_variational_quantum_algorithms/05_barren_plateaus.md](../docs/06_variational_quantum_algorithms/05_barren_plateaus.md), [06_noise_and_error_mitigation.md](../docs/06_variational_quantum_algorithms/06_noise_and_error_mitigation.md) — stretch
- Peruzzo et al. 2014 & O'Malley et al. 2016 — see the [reading ladder](../lesson-plans/12-reading-ladder.md), chapter 6 section
- `vqa-trainer` app for drilling the concepts before you build

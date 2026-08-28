# Companion Notebooks

Executable companions to the study suite in [`docs/`](../docs). Each chapter notebook
reproduces that chapter's key worked examples in runnable code — every printed number is
cross-checked (with assertions) against the corresponding docs file, so a notebook that runs
top-to-bottom is also a verification of the docs' arithmetic.

## How to run

All notebooks use the repository's virtualenv (`.venv`), which provides `qiskit`,
`qiskit-aer`, `numpy`, `scipy`, and `matplotlib`.

Option 1 — launch Jupyter from the venv:

```bash
cd /path/to/Quantum-Computing
source .venv/bin/activate
jupyter lab notebooks/
```

Option 2 — register the venv as a named kernel (usable from any Jupyter install):

```bash
.venv/bin/python -m ipykernel install --user --name quantum-study --display-name "Quantum Study (.venv)"
```

then pick the **Quantum Study (.venv)** kernel in Jupyter.

Headless execution of every notebook:

```bash
for nb in notebooks/*.ipynb; do
  MPLBACKEND=Agg .venv/bin/jupyter execute --inplace "$nb"
done
```

All random experiments use fixed seeds, so results are reproducible run-to-run.

## Notebook inventory

| Notebook | Companion to | Examples reproduced |
|----------|--------------|---------------------|
| [`ch01.ipynb`](ch01.ipynb) | `docs/01_mathematical_foundations` | Hadamard spectral decomposition; Pauli-basis expansion (`A = 2X+Z`); the √X gate (`V² = X`, eigenvalues `{1, i}`); partial trace of Bell and W states; purity/entropy entanglement test |
| [`ch02.ipynb`](ch02.ipynb) | `docs/02_quantum_mechanics` | Bloch dynamics of `(√3\|0⟩+i\|1⟩)/2` under S and H; Rabi oscillations (formula vs. RK4, transmon numbers); phase damping of `\|+⟩` + entropy `H(p)`; trace distance/fidelity + Fuchs–van de Graaff; Lindblad → Bloch equations, `T₂ ≤ 2T₁` budget |
| [`ch03.ipynb`](ch03.ipynb) | `docs/03_quantum_gates_and_circuits` | Gate-identity verification (`HXH=Z`, `TXT†=(X+Y)/√2`, …); `HTH = e^{iπ/8}R_x(π/4)` and the `H·S†·H` decomposition; {H,T} density (THTH irrational angle) experiment; stabilizer tracking (Bell circuit, `H^⊗3`); error composition + Ross–Selinger T-count budget |
| [`ch04.ipynb`](ch04.ipynb) | `docs/04_quantum_algorithms` | Full Grover simulation `N=16` (`k*=3`, `P≈0.961`); QPE of `φ=1/4` (`U=S`) and non-dyadic `φ=1/8`; HHL 2×2 (`P(1)=5/8`, `\|x⟩=(3\|0⟩+\|1⟩)/√10`); BB84 intercept-resend QBER Monte Carlo + Shor–Preskill key rate |
| [`ch05.ipynb`](ch05.ipynb) | `docs/05_quantum_error_correction` | 3-qubit repetition code GF(2) syndrome table (+ 2-flip failure mode); Shor [[9,1,3]] syndromes (`Y₄`, `X₁X₄X₇`); Steane [[7,1,3]] Hamming machinery (`HHᵀ=0`, syndrome = error position, weight structure); surface-code `p_L` scaling plot; repetition-code Monte Carlo |
| [`ch06.ipynb`](ch06.ipynb) | `docs/06_variational_quantum_algorithms` | H₂ VQE landscape `E(θ)` (exact `E₀=−1.857275` Ha, HF point, under-expressive ansatz); parameter-shift vs. finite differences + QFIM; QAOA MaxCut on triangle+pendant graph (`F₁*=2.713` at `(0.652,1.901)`); QAOA on `C₅` (`F₁*=3.75`) |
| [`ch07.ipynb`](ch07.ipynb) | `docs/07_quantum_hardware` | Transmon design parameters (5 GHz/−200 MHz and 4.5 GHz/−250 MHz specs, thermal occupation); T₁/Ramsey decay-curve fits; RB analysis of the docs dataset (`p=0.9936`, `r=0.32%`); interleaved RB gate error |
| [`ch08.ipynb`](ch08.ipynb) | `docs/08_advanced_topics` | Exact 2-site TFIM (`E₀=−√5`); first/second-order Trotter error scaling for the 4-site TFIM (with rigorous bound); entanglement entropy of Bell/partially-entangled states; negative conditional entropy + Holevo bound |
| [`noise_labs.ipynb`](noise_labs.ipynb) | `docs/02.../05`, `docs/07.../04` | Aer noise-model laboratory: channel zoo (amplitude damping, depolarizing, thermal relaxation vs. closed forms); simulated T₁ inversion-recovery experiment + exponential fit; Ramsey T₂ experiment + damped-cosine fit; 1-qubit randomized benchmarking (`random_clifford` sequences + inverse, `A·pᵐ+B` fit, error-per-Clifford vs. injected noise) |

## Conventions

- Docs qubit labels (`q₁, q₂, …`, big-endian in formulas) are mapped explicitly in each cell;
  where qiskit's little-endian ordering matters, the code says so.
- Assertions use the docs' printed precision (typically 3–6 significant figures).
- Plots use matplotlib only; no styling dependencies.

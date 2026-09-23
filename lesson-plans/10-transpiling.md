# Transpiling for Quantum Computing

## Goal
Gain deep expertise in quantum circuit transpilation — the compilation process that maps abstract circuits to hardware-executable form — including routing, gate synthesis, optimization passes, and custom pass development.

---

## Module 1 — What Is Transpilation?

**Objective:** Understand the full transpilation pipeline and why it is essential for running on real quantum hardware.

### The Problem

Abstract quantum circuits specify *what* to compute, not *how* to run it on a specific chip. Hardware imposes:

| Constraint | Example |
|---|---|
| Native gate set | `{CZ, RZ, SX, X}` on current IBM Heron devices; `{ECR, RZ, SX, X}` on Eagle; `{CX, RZ, SX, X}` on older (retired) Falcon devices |
| Qubit connectivity | Not all-to-all; defined by coupling map |
| Gate fidelity variation | Some two-qubit pairs have much better fidelity |
| Calibration drift | Gates are recalibrated daily |
| Circuit depth limits | Coherence time sets max depth |

### The Pipeline (Qiskit)

```
Abstract Circuit
       │
  [Translation]    — decompose gates into basis gates
       │
  [Routing]        — insert SWAP gates to satisfy connectivity
       │
  [Optimization]   — minimize gate count and depth
       │
  [Scheduling]     — assign timing to parallel gates
       │
Hardware-Ready ISA Circuit
```

---

## Module 2 — Basis Translation

**Objective:** Decompose arbitrary unitaries into a hardware's native gate set.

### Standard Decompositions

**Single-qubit decomposition (ZYZ):**
Any U ∈ SU(2) can be written:
```
U = e^(iα) Rz(β) Ry(γ) Rz(δ)
```

**IBM native gate sets by hardware generation:**

| Generation | Two-qubit basis | Full basis set |
|---|---|---|
| Heron (current: ibm_torino, ibm_fez, …) | CZ | `{CZ, RZ, SX, X}` |
| Eagle (ibm_brisbane, ibm_sherbrooke, …) | ECR (echoed cross-resonance) | `{ECR, RZ, SX, X}` |
| Falcon (retired) — historical note | CX | `{CX, RZ, SX, X}` |

The decompositions below use the historical CX basis for readability; on ECR/CZ hardware the transpiler produces the analogous ECR/CZ decompositions (CX itself costs one ECR or CZ plus single-qubit gates).

| Abstract Gate | Native Decomposition |
|---|---|
| H | `RZ(π/2) · SX · RZ(π/2)` |
| S | `RZ(π/2)` |
| T | `RZ(π/4)` |
| SWAP | 3× CX (or 3× iSWAP) |
| CZ | `H · CX · H` |
| Toffoli | 6× CNOT + single-qubit gates |

**Solovay-Kitaev for discrete gate sets:**
- Any single-qubit U can be approximated to error ε using O(log^c(1/ε)) gates from {H, T, CNOT}
- c ≈ 3.97 in practice (improved to ~1.5 with modern variants)
- Use for fault-tolerant contexts where only Clifford + T is available

**In Qiskit:**
```python
from qiskit import transpile

# Decompose to IBM basis
qc_t = transpile(qc, basis_gates=['cx', 'rz', 'sx', 'x'])
print(qc_t.count_ops())
```

**Exercises:**
- Manually decompose a Toffoli gate into {CX, H, T, Tdg}

  <details><summary>Solution</summary>

  **Where the construction comes from.** Toffoli applies a phase `-1` only on
  `|111⟩`, i.e. it is `H · CCZ · H` on the target. Expanding
  `CCZ = exp(iπ(1-Z₀)(1-Z₁)(1-Z₂)/8)` gives a sum of three single-`Z`, three `ZZ`
  and one `ZZZ` rotation, all by `±π/4`. Each `Z`-type rotation is a `T` or `Tdg`
  conjugated by CNOTs, and sharing those CNOTs across the terms yields the standard
  6-CNOT, 7-T circuit:

  ```python
  from qiskit import QuantumCircuit

  tof = QuantumCircuit(3, name="toffoli_6cx")
  tof.h(2)
  tof.cx(1, 2); tof.tdg(2)
  tof.cx(0, 2); tof.t(2)
  tof.cx(1, 2); tof.tdg(2)
  tof.cx(0, 2); tof.t(1); tof.t(2)
  tof.h(2)
  tof.cx(0, 1); tof.t(0); tof.tdg(1)
  tof.cx(0, 1)
  print(tof.count_ops())
  ```

  Drawn:

  ```
                                                       ┌───┐
  q_0: ───────────────────■─────────────────────■────■─┤ T ├─■──
                          │             ┌───┐   │  ┌─┴─┐┌──┴┐┌┴─┐
  q_1: ───────■───────────┼─────────■───┤ T ├───┼──┤ X ├┤Tdg├┤X ├
       ┌───┐┌─┴─┐┌─────┐┌─┴─┐┌───┐┌─┴─┐┌┴───┴┐┌─┴─┐├───┤├───┤└──┘
  q_2: ┤ H ├┤ X ├┤ Tdg ├┤ X ├┤ T ├┤ X ├┤ Tdg ├┤ X ├┤ T ├┤ H ├────
       └───┘└───┘└─────┘└───┘└───┘└───┘└─────┘└───┘└───┘└───┘
  count_ops: OrderedDict({'cx': 6, 't': 4, 'tdg': 3, 'h': 2})
  ```

  **The resource counts to remember.** 6 CNOTs, 7 T gates, 2 Hadamards, **T-depth 3**.
  Six CNOTs is optimal for an exact ancilla-free Toffoli, and so is T-count 7; the
  T-count drops to 4 if you allow one clean ancilla and a measurement-based
  uncomputation (the "temporary logical-AND" of Gidney 2018), which is why
  fault-tolerant cost models count Toffolis rather than T gates.

  </details>

- Verify your decomposition using Qiskit's `Operator` equivalence check

  <details><summary>Solution</summary>

  ```python
  from qiskit import QuantumCircuit
  from qiskit.quantum_info import Operator
  import numpy as np

  ref = QuantumCircuit(3); ref.ccx(0, 1, 2)
  print("equivalent (up to global phase)?", Operator(tof).equiv(Operator(ref)))
  print("exactly equal (no phase slack)?",
        np.allclose(Operator(tof).data, Operator(ref).data))
  ```

  Real output:

  ```
  equivalent (up to global phase)? True
  exactly equal (no phase slack)? True
  ```

  **Three things worth knowing about this check.**

  - `Operator.equiv` allows an arbitrary *global* phase; `np.allclose` on the
    matrices does not. A decomposition that is only `equiv` is still correct as a
    standalone circuit, but if you intend to use it inside a `.control()` the global
    phase becomes a *relative* phase and the controlled version will be wrong. This
    Toffoli circuit is exact, so it is safe to control.
  - `Operator(qc)` builds the full `2ⁿ × 2ⁿ` matrix, so it is only usable up to about
    12–14 qubits. Above that, compare on random input states with
    `Statevector.from_int(...).evolve(...)`, or use
    `qiskit.quantum_info.process_fidelity` on small blocks.
  - After a *transpile with a coupling map* the naive comparison fails, because the
    transpiler is allowed to permute qubits. Use `Operator.from_circuit(t)`, which
    reads `t.layout` and undoes both the initial and the final permutation.

  </details>

- Count the CX depth of a 3-qubit QFT after basis translation

  <details><summary>Solution</summary>

  ```python
  from qiskit import QuantumCircuit, transpile
  from qiskit.circuit.library import QFTGate

  qft3 = QuantumCircuit(3)
  qft3.append(QFTGate(3), range(3))
  for basis in (['cx','rz','sx','x'], ['cz','rz','sx','x'], ['ecr','rz','sx','x']):
      for lvl in (0, 3):
          t = transpile(qft3, basis_gates=basis, optimization_level=lvl,
                        seed_transpiler=7)
          two = [g for g in basis if g in ('cx', 'cz', 'ecr')][0]
          print(basis[0], lvl, dict(t.count_ops()), "depth", t.depth(),
                f"{two}-depth", t.depth(lambda i: i.operation.name == two))
  ```

  Real output (all-to-all connectivity, so no routing SWAPs are inserted):

  ```
  abstract: {'p': 9, 'cx': 9, 'u': 3} depth 18
    basis=cx  opt=0: {'rz': 15, 'cx': 9, 'sx': 3}           depth=22  cx-depth=9
    basis=cx  opt=3: {'rz': 10, 'cx': 6, 'sx': 3}           depth=16  cx-depth=6
    basis=cz  opt=0: {'rz': 39, 'sx': 21, 'cz': 9}          depth=52  cz-depth=9
    basis=cz  opt=3: {'rz': 15, 'sx': 15, 'cz': 6, 'x': 2}  depth=26  cz-depth=6
    basis=ecr opt=0: {'rz': 48, 'sx': 12, 'ecr': 9, 'x': 6} depth=48  ecr-depth=9
    basis=ecr opt=3: {'rz': 24, 'sx': 15, 'ecr': 6, 'x': 3} depth=33  ecr-depth=6
  ```

  **Where the 9 comes from.** A 3-qubit QFT is 3 Hadamards, 3 controlled-phase gates
  (`CP(π/2)` twice, `CP(π/4)` once) and the final bit-reversal SWAP:

  ```
  3 × CP   = 3 × 2 CX = 6 CX
  1 × SWAP =       3 CX = 3 CX
                  ------------
                         9 CX,  and since every one acts on the same chain of
                                qubits, the CX depth is 9 as well
  ```

  In general an `n`-qubit QFT needs `n(n-1)/2` controlled-phase gates — `n(n-1)` CX —
  plus `3⌊n/2⌋` CX for the swaps.

  **Why level 3 reports 6 and not 9.** With no coupling map, the `ElidePermutations`
  pass (level ≥ 2) deletes the bit-reversal SWAP outright and records the relabelling
  in `t.layout.final_index_layout()`. The swaps really are free — on hardware you get
  the same saving by reversing the classical bit order when you read the counts.

  **The invariant to notice.** The two-qubit *count* is the same in all three bases:
  `CZ` and `ECR` are each locally equivalent to `CX`, so the entangling cost cannot
  change — only the single-qubit dressing does (15 `rz` for CX, 39 for CZ, 48 for
  ECR at level 0), and level 3 roughly halves that.

  </details>

---

## Module 3 — Qubit Routing

**Objective:** Map logical qubits to physical qubits satisfying the hardware coupling map.

### The Problem

A two-qubit gate `CX(q0, q1)` requires q0 and q1 to be physically adjacent. If they're not, insert SWAPs to move them together.

**SWAP cost:** 3 CX gates — expensive!

### Routing Algorithms

| Algorithm | Strategy | Quality | Speed |
|---|---|---|---|
| Stochastic SWAP | Random SWAP insertion + scoring (pass removed in Qiskit 2.0) | Good | Fast |
| SABRE | Lookahead heuristic, bidirectional | Better | Moderate |
| SABRE (v2) | Improved heuristic | State of the art | Moderate |
| Exact (ILP) | Integer linear program, optimal | Optimal | Slow (small circuits) |
| Basic | Greedy, suboptimal | Poor | Very fast |

### SABRE Algorithm

1. Compute front layer (gates ready to execute)
2. Score each candidate SWAP by how much it reduces future gate distances
3. Apply best SWAP, update front layer
4. Repeat until all gates are routed

**Layout strategies:**
- **Trivial layout:** Map qubit i → physical qubit i (rarely optimal)
- **Dense layout:** Place qubits near graph center
- **SABRE layout:** Use routing heuristic to find good initial layout
- **VF2 layout:** Graph isomorphism to find subgraph match

```python
from qiskit import transpile
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2

# FakeNairobiV2 models the retired 7-qubit Nairobi device (CX basis) —
# useful offline, but current IBM devices are ECR- or CZ-based.
backend = FakeNairobiV2()

# Full transpile with SABRE routing
qc_t = transpile(
    qc,
    backend=backend,
    routing_method='sabre',
    layout_method='sabre',
    optimization_level=3
)

# Inspect final layout
print(qc_t.layout)
print(qc_t.count_ops())
```

**Exercises:**
- Draw the coupling map for FakeNairobiV2 and manually route a 3-qubit circuit

  <details><summary>Solution</summary>

  **The coupling map.** Read it off the backend rather than trusting a picture:

  ```python
  from qiskit_ibm_runtime.fake_provider import FakeNairobiV2

  backend = FakeNairobiV2()
  print(backend.num_qubits)
  print(sorted({tuple(sorted(e)) for e in backend.coupling_map.get_edges()}))
  print(backend.operation_names)
  ```

  ```
  7
  [(0, 1), (1, 2), (1, 3), (3, 5), (4, 5), (5, 6)]
  ['for_loop', 'id', 'switch_case', 'reset', 'rz', 'measure', 'cx', 'x', 'delay', 'if_else', 'sx']
  ```

  That is the classic IBM "H" layout — two degree-3 hubs (`Q1` and `Q5`) joined by
  the `1–3–5` spine:

  ```
        Q0        Q4
         |         |
        Q1 -- Q3 -- Q5 -- Q6
         |
        Q2
  ```

  **Manual routing.** Take a CX triangle, `H(q0); CX(q0,q1); CX(q0,q2); CX(q1,q2)`,
  and route it onto the sub-path `Q0 – Q1 – Q2`.

  *Bad layout.* With the trivial map `qᵢ → Qᵢ`, `CX(q0,q2)` needs `Q0–Q2`, which is
  not an edge; after swapping to fix it, `CX(q1,q2)` breaks, so you pay **2 SWAPs**
  (3 CX each) for a total of 9 CX.

  *Good layout.* Put the *hub* of the interaction graph on the *hub* of the device:
  `q0 → Q1`, `q1 → Q0`, `q2 → Q2`. Now

  ```
  CX(q0,q1)  ->  Q1–Q0   edge     ok
  CX(q0,q2)  ->  Q1–Q2   edge     ok
  CX(q1,q2)  ->  Q0–Q2   not an edge  ->  SWAP(Q0,Q1), then CX on Q1–Q2
  ```

  one SWAP, 6 CX total, verified equivalent to the original with
  `Operator(...).equiv(...)`. SABRE finds the same 6 CX when restricted to that
  three-qubit line.

  **Two refinements worth internalising.**

  - A CNOT immediately followed by a SWAP on the same pair costs **2** CX, not 4:
    `CX(a,b) · SWAP(a,b) = CX(b,a) · CX(a,b)` (checked with `Operator.equiv`). Good
    routers exploit this, which is why `optimization_level=3` on the full Nairobi
    device lands at **4** CX, using the degree-3 hub `Q1` and merging the last CNOT
    into the SWAP.
  - Routing quality is dominated by the *initial layout*, not the SWAP-insertion
    heuristic. Matching the busiest logical qubit to the highest-degree physical
    qubit is most of the win.

  </details>

- Compare SWAP overhead for trivial vs SABRE layout on a 5-qubit GHZ circuit

  <details><summary>Solution</summary>

  A 5-qubit GHZ has a star interaction graph: `q0` talks to all of `q1…q4`. No
  physical qubit on Nairobi has degree 4, so SWAPs are unavoidable — the question is
  how many.

  ```python
  from qiskit import QuantumCircuit, transpile
  from qiskit_ibm_runtime.fake_provider import FakeNairobiV2

  backend = FakeNairobiV2()
  ghz = QuantumCircuit(5); ghz.h(0)
  for i in range(4):
      ghz.cx(0, i + 1)

  for name, kw in [("trivial", dict(initial_layout=[0, 1, 2, 3, 4])),
                   ("sabre",   dict(layout_method='sabre'))]:
      t = transpile(ghz, backend=backend, routing_method='sabre',
                    optimization_level=0, seed_transpiler=11, **kw)
      cx = t.count_ops().get('cx', 0)
      print(name, "cx =", cx, " extra swaps =", (cx - 4) // 3,
            " depth =", t.depth())
  ```

  Real output:

  ```
  abstract GHZ-5: OrderedDict({'cx': 4, 'h': 1}) depth 5
  trivial (q_i -> Q_i)   cx= 13  depth= 16  extra swaps = 3
  sabre                  cx=  7  depth=  8  extra swaps = 1
  ```

  **Reading it.** The trivial layout maps the star's hub onto `Q0`, which has degree
  1 — every other CNOT then has to be walked in, costing 3 SWAPs (9 extra CX) and
  tripling the depth. SABRE puts the hub on `Q1` (degree 3), so only the fourth
  neighbour needs a SWAP: 1 SWAP, 3 extra CX.

  `dense` layout sits in between (2 SWAPs, 10 CX), because it optimises for a
  well-connected *region* without knowing the circuit's interaction graph.

  **The number to carry away.** 9 extra CX versus 3 is a factor of three in the
  dominant error source, from nothing but the choice of starting permutation. On a
  device with a `1%` CX error that is the difference between roughly `0.88` and
  `0.94` expected fidelity for the entangling layer alone. Layout is not a
  micro-optimisation.

  </details>

- Implement a greedy routing algorithm from scratch

  <details><summary>Solution</summary>

  The minimal greedy router: walk the circuit in order; when a two-qubit gate lands
  on a non-adjacent pair, BFS the shortest path between them and SWAP one endpoint
  along it until the two touch. Everything else is bookkeeping on the
  logical→physical map.

  ```python
  from collections import deque
  from qiskit import QuantumCircuit

  def bfs_path(edges, n, a, b):
      """Shortest path a -> b in the coupling graph, as a list of physical qubits."""
      adj = {i: set() for i in range(n)}
      for u, v in edges:
          adj[u].add(v); adj[v].add(u)
      prev = {a: None}; queue = deque([a])
      while queue:
          u = queue.popleft()
          if u == b:
              break
          for w in adj[u]:
              if w not in prev:
                  prev[w] = u; queue.append(w)
      path = [b]
      while path[-1] != a:
          path.append(prev[path[-1]])
      return path[::-1]

  def greedy_route(circ, edges, n_phys):
      """Route `circ` onto `edges` with a trivial initial layout."""
      out = QuantumCircuit(n_phys)
      log2phys = {i: i for i in range(circ.num_qubits)}
      eset = {frozenset(e) for e in edges}

      def apply_swap(u, v):
          out.swap(u, v)
          inv = {p: l for l, p in log2phys.items()}
          lu, lv = inv.get(u), inv.get(v)
          if lu is not None: log2phys[lu] = v
          if lv is not None: log2phys[lv] = u

      for inst in circ.data:
          qs = [circ.find_bit(q).index for q in inst.qubits]
          if len(qs) == 1:
              out.append(inst.operation, [log2phys[qs[0]]])
              continue
          a, b = log2phys[qs[0]], log2phys[qs[1]]
          if frozenset((a, b)) not in eset:
              path = bfs_path(edges, n_phys, a, b)
              for u, v in zip(path, path[1:-1]):   # walk a toward b, stop adjacent
                  apply_swap(u, v)
              a, b = log2phys[qs[0]], log2phys[qs[1]]
          out.append(inst.operation, [a, b])
      return out, log2phys
  ```

  Running it on the GHZ-5 circuit with Nairobi's edge list
  `[(0,1),(1,2),(1,3),(3,5),(4,5),(5,6)]` and a trivial initial layout:

  ```
  greedy                                 : OrderedDict({'cx': 4, 'swap': 3, 'h': 1})  depth 8
  greedy + restoring the identity mapping: OrderedDict({'cx': 4, 'swap': 6, 'h': 1})  depth 11
  all 2q gates on coupling-map edges?    : True
  unitary matches the original?          : True   (Operator equivalence, restore variant)
  SABRE, same trivial layout             : 3 swaps
  SABRE, free layout                     : 1 swap
  ```

  **What the experiment teaches.**

  - Greedy *matches* SABRE when both start from the trivial layout. Greedy routing
    is not the weak link — the **initial layout** is. SABRE's 1 SWAP comes from
    choosing a better starting permutation, not a cleverer SWAP rule.
  - Restoring the identity permutation at the end *doubles* the SWAP count. Do not
    do it: record the final permutation and relabel classical bits at read-out
    instead. That is exactly what `final_index_layout()` and `ElidePermutations`
    exist for.
  - Greedy is myopic: it optimises the gate in front of it. SABRE adds a lookahead
    term that also scores the next few layers, plus forward/backward passes that let
    a good routing decision propagate back into the initial layout.

  Always verify a hand-written router two ways — every two-qubit gate on a real
  edge, and the overall unitary unchanged once the permutation is undone.

  </details>

---

## Module 4 — Circuit Optimization Passes

**Objective:** Apply algebraic and peephole optimizations to reduce gate count and depth.

### Categories of Optimization

**1. Cancellation and Merging**
- `X · X = I` → remove both
- `CX · CX = I` → remove both
- Consecutive Rz gates → merge: `Rz(a) · Rz(b) = Rz(a+b)`

**2. Commutation Rules**
- `Rz(θ) · CX(ctrl, tgt)` = `CX(ctrl, tgt) · Rz(θ)` if Rz on control
- Use commutation to reorder gates for cancellation opportunities

**3. Template Matching**
- Search for subsequences that match known equivalent but cheaper templates
- E.g., replace 3-CNOT SWAP with iSWAP where available

**4. Clifford Optimization**
- Clifford circuits have O(n²/log n) optimal size; tableau simulation
- Peephole optimization on Clifford subcircuits

**5. KAK Decomposition (two-qubit)**
- Any 2-qubit unitary = (local A) · exp(iΣ cᵢ σᵢ⊗σᵢ) · (local B)
- Exactly 3 CX gates suffice for generic 2-qubit gate; sometimes 2 or 1
- Implemented in Qiskit as `UnitarySynthesis`

```python
from qiskit.transpiler.passes import (
    Optimize1qGatesDecomposition,
    InverseCancellation,   # replaces CXCancellation, removed in Qiskit 2.0
    CommutativeCancellation,
    ConsolidateBlocks,
    UnitarySynthesis,
)
from qiskit.circuit.library import CXGate

# Cancel adjacent CX·CX = I pairs (and any other self-inverse gates you list)
cx_cancel = InverseCancellation([CXGate()])
```

**Exercises:**
- Apply `InverseCancellation([CXGate()])` manually to a circuit with redundant CNOTs

  <details><summary>Solution</summary>

  ```python
  from qiskit import QuantumCircuit
  from qiskit.circuit.library import CXGate, HGate
  from qiskit.transpiler import PassManager
  from qiskit.transpiler.passes import InverseCancellation
  from qiskit.quantum_info import Operator

  redundant = QuantumCircuit(3)
  redundant.h(0)
  redundant.cx(0, 1); redundant.cx(0, 1)     # adjacent pair: cancels
  redundant.cx(1, 2)
  redundant.h(2); redundant.h(2)             # adjacent pair: cancels
  redundant.cx(1, 2)                         # only adjacent *after* the H's go
  redundant.cx(0, 2)
  print("before:", dict(redundant.count_ops()), "depth", redundant.depth())

  pm = PassManager([InverseCancellation([CXGate(), HGate()])])
  out = pm.run(redundant)
  print("after :", dict(out.count_ops()), "depth", out.depth())
  print("same unitary?", Operator(redundant).equiv(Operator(out)))
  ```

  Real output:

  ```
  before: {'cx': 5, 'h': 3} depth 8
  after : {'cx': 3, 'h': 1} depth 3
  same unitary? True
  ```

  **The instructive part is what did *not* cancel.** The two `cx(1,2)` gates are
  separated by `h(2); h(2)`. `InverseCancellation` makes a *single* forward sweep of
  the DAG, so it removes the Hadamard pair, but by the time it does, it has already
  passed the first `cx(1,2)` — the now-adjacent CX pair survives:

  ```
        ┌───┐
  q_0: ─┤ H ├───────■──
        └───┘       │
  q_1: ───■────■────┼──
        ┌─┴─┐┌─┴─┐┌─┴─┐
  q_2: ─┤ X ├┤ X ├┤ X ├
        └───┘└───┘└───┘
  ```

  Cancellation is not a fixed point after one pass. Either run the pass repeatedly
  (see the `DoWhileController` exercise in Module 5) or use
  `CommutativeCancellation`, which reasons about commutation relations rather than
  strict adjacency and would have caught this in one sweep.

  **API note.** `CXCancellation` was removed in Qiskit 2.0. `InverseCancellation`
  takes a *list of self-inverse gates* (or `(gate, inverse)` pairs) and cancels
  adjacent occurrences of each — so pass every gate you care about,
  `[CXGate(), HGate(), XGate(), CZGate(), (TGate(), TdgGate())]`, not just `CXGate()`.

  </details>

- Verify that KAK decomposition of a SWAP uses exactly 3 CX gates

  <details><summary>Solution</summary>

  **The theory.** Every two-qubit unitary factorises (KAK / Cartan) as

  ```
  U = (A₁ ⊗ A₂) · exp( i(a XX + b YY + c ZZ) ) · (B₁ ⊗ B₂)
  ```

  with local unitaries `A`, `B` and *interaction coordinates* `(a,b,c)` in the Weyl
  chamber `π/4 ≥ a ≥ b ≥ |c|`. The minimum number of CX gates needed is fixed by
  those coordinates alone: 0 if `(0,0,0)`, 1 if `b = c = 0`, 2 if `c = 0`, else 3.

  ```python
  from qiskit import QuantumCircuit
  from qiskit.circuit.library import CXGate
  from qiskit.quantum_info import Operator
  from qiskit.synthesis import TwoQubitBasisDecomposer, TwoQubitWeylDecomposition

  dec = TwoQubitBasisDecomposer(CXGate())
  for label, method in [('CX','cx'), ('CZ','cz'), ('iSWAP','iswap'), ('SWAP','swap')]:
      circ = QuantumCircuit(2); getattr(circ, method)(0, 1)
      U = Operator(circ).data
      w = TwoQubitWeylDecomposition(U)
      print(label, (round(w.a,6), round(w.b,6), round(w.c,6)),
            "CX cost =", dec.num_basis_gates(U))
  ```

  Real output (`π/4 = 0.785398`):

  ```
  CX    Weyl=(0.785398, 0.000000, 0.000000)  CX cost=1
  CZ    Weyl=(0.785398, 0.000000, 0.000000)  CX cost=1
  iSWAP Weyl=(0.785398, 0.785398, 0.000000)  CX cost=2
  SWAP  Weyl=(0.785398, 0.785398, 0.785398)  CX cost=3
  ```

  SWAP sits at the far corner `(π/4, π/4, π/4)` of the Weyl chamber — all three
  interaction coordinates maximal — which is exactly the condition for needing the
  full three CX. Synthesising it confirms the count:

  ```
  dec(Operator(swap).data).count_ops() -> OrderedDict({'u': 8, 'cx': 3})
  Operator(...).equiv(Operator(swap))  -> True
  ```

  **A trap to know about.** Asking the *transpiler* instead of the decomposer gives a
  surprise:

  ```
  transpile(swap, basis_gates=['cx','rz','sx','x'], optimization_level=0) -> {'cx': 3}
  transpile(swap, basis_gates=['cx','rz','sx','x'], optimization_level=2) -> {}
  ```

  At level ≥ 2 the `ElidePermutations` pass recognises that a SWAP with no
  connectivity constraint is a pure relabelling and deletes it, recording the
  permutation in `circuit.layout.final_index_layout()`. Three CX is the cost of
  *performing* a SWAP; zero is the cost of *pretending* you did one. On hardware the
  SWAPs inserted by routing are real, and the KAK bound of 3 CX applies.

  </details>

- Build a circuit, run through optimization level 3, and count the gate reduction

  <details><summary>Solution</summary>

  ```python
  from qiskit import transpile
  from qiskit.circuit.random import random_circuit
  from qiskit.quantum_info import Operator

  rc = random_circuit(5, 20, max_operands=2, seed=1234)
  for lvl in range(4):
      t = transpile(rc, basis_gates=['cx','rz','sx','x'],
                    optimization_level=lvl, seed_transpiler=5)
      ops = dict(t.count_ops())
      print(f"opt{lvl}: cx={ops.get('cx',0):3d} total={sum(ops.values()):4d} "
            f"depth={t.depth():3d}")
  ```

  Real output for a 5-qubit, depth-20 random circuit:

  | level | CX | total gates | depth |
  |---|---|---|---|
  | 0 | 43 | 343 | 132 |
  | 1 | 39 | 195 | 90 |
  | 2 | 28 | 166 | 71 |
  | 3 | 28 | 165 | 71 |

  **CX reduction 43 → 28, a 35% saving; total gates 343 → 165, a 52% saving.**

  **Where each level's saving comes from.**

  - Level 0 is pure translation: every abstract gate is expanded in place, so the
    count is just the sum of the individual decompositions.
  - Level 1 adds `Optimize1qGatesDecomposition` — neighbouring single-qubit gates
    merge into one `rz–sx–rz–sx–rz` Euler sequence. That is why the total halves but
    the CX count barely moves.
  - Level 2 adds `ConsolidateBlocks` + `UnitarySynthesis`: contiguous two-qubit
    blocks are multiplied into a single 4×4 unitary and re-synthesised via KAK with
    the minimum number of CX. This is where the two-qubit saving lives.
  - Level 3 adds heavier resynthesis and more `CommutativeCancellation`; on a random
    circuit there is almost nothing left for it, so the gain is a single gate. Level
    3 is worth its extra compile time on *structured* circuits (QFT, Trotter steps,
    ansätze), not on random ones.

  **Verification gotcha.** The naive check fails:

  ```
  Operator(t3).equiv(Operator(qc))               -> False
  Operator.from_circuit(t3).equiv(Operator(qc))  -> True
  ```

  because level ≥ 2 elided permutations and reported them in
  `t3.layout.final_index_layout()` — here `[1, 2, 0, 3, 4]`. `Operator.from_circuit`
  reads the layout and undoes both the initial and the final permutation; plain
  `Operator` does not. Any "the optimiser broke my circuit" bug report should start
  here.

  </details>

---

## Module 5 — The Qiskit Transpiler Pass Manager

**Objective:** Understand and customize the Qiskit pass manager to build tailored compilation pipelines.

### Pass Types

| Pass Type | Description |
|---|---|
| `TransformationPass` | Modifies the circuit (routing, optimization) |
| `AnalysisPass` | Computes properties, stores in `property_set` |
| `ConditionalController` | Run passes conditionally |
| `DoWhileController` | Repeat passes until convergence |

### Built-in Optimization Levels

| Level | What It Does |
|---|---|
| 0 | Only mapping (routing + translation); no optimization |
| 1 | Light optimization: trivial cancellation |
| 2 | Medium: commutation, Clifford optimization |
| 3 | Heavy: full KAK + template matching + Clifford synthesis |

### Custom Pass Manager

```python
from qiskit.circuit.library import CXGate
from qiskit.transpiler import PassManager, CouplingMap
from qiskit.transpiler.passes import (
    SabreLayout,
    SabreSwap,
    BasisTranslator,
    Optimize1qGatesDecomposition,
    InverseCancellation,
)
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as sel

coupling_map = CouplingMap.from_line(5)

pm = PassManager([
    # Layout — SabreLayout applies the layout itself and also performs
    # routing by default (no separate ApplyLayout needed)
    SabreLayout(coupling_map, max_iterations=3, seed=42),
    # Routing — explicit stage; a no-op here if SabreLayout already routed
    SabreSwap(coupling_map, heuristic='decay', seed=42),
    # Translation
    BasisTranslator(sel, ['cx', 'rz', 'sx', 'x']),
    # Optimization
    Optimize1qGatesDecomposition(basis=['rz', 'sx', 'x']),
    InverseCancellation([CXGate()]),
])

qc_t = pm.run(qc)
```

For standard pipelines, prefer the preset builder — it is what `transpile()` uses internally and is required knowledge for the runtime-primitives (ISA circuit) workflow:

```python
from qiskit.transpiler import generate_preset_pass_manager

# backend: a BackendV2 (from QiskitRuntimeService or a fake provider);
# alternatively pass coupling_map=... and basis_gates=... directly
pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
qc_isa = pm.run(qc)
```

### Writing a Custom Pass

```python
from qiskit.transpiler.basepasses import TransformationPass
from qiskit.dagcircuit import DAGCircuit, DAGOpNode

class RemoveDoubleX(TransformationPass):
    """Cancel adjacent pairs of X gates on the same qubit."""

    def run(self, dag: DAGCircuit) -> DAGCircuit:
        # Collect pairs first, then remove: never mutate the DAG while
        # iterating it, and never remove the same node twice.
        matched = set()
        pairs = []
        for node in dag.topological_op_nodes():
            if node in matched or node.op.name != 'x':
                continue
            for succ in dag.successors(node):
                # Successors include wire/output nodes, so check the type
                # with isinstance (the old `node.type == 'op'` API is gone)
                if (isinstance(succ, DAGOpNode) and succ not in matched
                        and succ.op.name == 'x' and succ.qargs == node.qargs):
                    pairs.append((node, succ))
                    matched.update((node, succ))
                    break
        for node, succ in pairs:
            dag.remove_op_node(node)
            dag.remove_op_node(succ)
        return dag
```

**Exercises:**
- Build a pass manager that only performs routing and translation, no optimization

  <details><summary>Solution</summary>

  Strip the pipeline to the two mandatory stages — get the gates onto real edges,
  and get them into the native basis — and nothing else. Anything that rewrites
  gates for cost reasons is optimisation and stays out.

  ```python
  from qiskit import QuantumCircuit
  from qiskit.transpiler import PassManager, CouplingMap
  from qiskit.transpiler.passes import SabreLayout, BasisTranslator
  from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as sel

  cmap = CouplingMap.from_line(5)
  ghz = QuantumCircuit(5)
  ghz.h(0)
  for i in range(4):
      ghz.cx(0, i + 1)

  pm_map_only = PassManager([
      SabreLayout(cmap, max_iterations=3, seed=42),   # layout *and* routing
      BasisTranslator(sel, ['cx', 'rz', 'sx', 'x']),  # translation
  ])
  mapped = pm_map_only.run(ghz)
  print(dict(mapped.count_ops()), "depth", mapped.depth())
  ```

  Real output:

  ```
  routing+translation only: {'cx': 10, 'rz': 2, 'sx': 1} depth 13
  2q gates all on line edges? True
  ```

  **Three things to get right.**

  - `SabreLayout` *already routes* (it runs `SabreSwap` internally across its
    iterations) and applies the layout itself. You do not need a separate
    `ApplyLayout`, and adding an explicit `SabreSwap` afterwards is a no-op on an
    already-routed circuit. If you want layout and routing genuinely separate, use
    `SabreLayout(..., skip_routing=True)` followed by `ApplyLayout()` and
    `SabreSwap(...)`.
  - The order matters: route *before* translating. Routing inserts SWAPs, which are
    not in the basis, so translation has to come last.
  - Compare against `generate_preset_pass_manager(optimization_level=0, backend=...)`
    — the preset level 0 is exactly this pipeline plus the housekeeping passes
    (`UnitarySynthesis`, `HighLevelSynthesis`, `CheckMap`), and is what you should
    actually use in production. Hand-rolling it is for understanding the stages.

  Always finish with an assertion rather than an eyeball: every two-qubit
  instruction's qubit pair must be in `cmap.get_edges()`, and every operation name
  must be in the target basis.

  </details>

- Write a custom pass that counts the number of T gates and stores in `property_set`

  <details><summary>Solution</summary>

  Counting is *analysis*, not transformation, so subclass `AnalysisPass` and write
  the result into `property_set`. An `AnalysisPass` must return the DAG unchanged.

  ```python
  from qiskit import QuantumCircuit
  from qiskit.transpiler import PassManager
  from qiskit.transpiler.basepasses import AnalysisPass

  class CountTGates(AnalysisPass):
      """Store the number of T / Tdg gates in property_set['t_count']."""

      def run(self, dag):
          self.property_set['t_count'] = sum(
              1 for node in dag.op_nodes() if node.op.name in ('t', 'tdg'))
          return dag

  toffoli = QuantumCircuit(3)
  toffoli.h(2)
  toffoli.cx(1, 2); toffoli.tdg(2)
  toffoli.cx(0, 2); toffoli.t(2)
  toffoli.cx(1, 2); toffoli.tdg(2)
  toffoli.cx(0, 2); toffoli.t(1); toffoli.t(2)
  toffoli.h(2)
  toffoli.cx(0, 1); toffoli.t(0); toffoli.tdg(1)
  toffoli.cx(0, 1)

  pm_t = PassManager([CountTGates()])
  pm_t.run(toffoli)
  print("T-count:", pm_t.property_set['t_count'])
  ```

  Real output:

  ```
  T-count of the 6-CX Toffoli: 7
  ```

  which is the known optimal ancilla-free T-count, and a good self-check on the
  Module 2 decomposition.

  **Points to note.**

  - Read the result off `pm.property_set` *after* `run()`; the property set is the
    pass manager's shared scratchpad, and the same dictionary is what
    `ConditionalController` and `DoWhileController` inspect. That is the whole
    mechanism behind conditional flow control.
  - Use `dag.op_nodes()`, not `dag.nodes()` — the latter includes the input/output
    wire nodes.
  - A realistic T-counter must also recurse into control-flow blocks
    (`node.op.blocks` for `IfElseOp`, `ForLoopOp`, …) and decide what to do with
    `rz(θ)` gates whose angle is not a multiple of `π/4`; those are not Clifford+T at
    all and need Solovay–Kitaev or Ross–Selinger synthesis before a T-count means
    anything.

  </details>

- Chain `DoWhileController` with `InverseCancellation([CXGate()])` until no further cancellation is possible

  <details><summary>Solution</summary>

  `InverseCancellation` sweeps the DAG once, so cascading cancellations need a loop.
  `DoWhileController` reruns a list of tasks while a predicate over `property_set`
  is true — so pair the cancellation pass with a tiny analysis pass that records the
  DAG size, and loop until the size stops changing.

  ```python
  from qiskit import QuantumCircuit
  from qiskit.circuit.library import CXGate, HGate
  from qiskit.transpiler import PassManager
  from qiskit.transpiler.passes import InverseCancellation
  from qiskit.transpiler.basepasses import AnalysisPass
  from qiskit.passmanager import DoWhileController
  from qiskit.quantum_info import Operator

  class RecordSize(AnalysisPass):
      def run(self, dag):
          self.property_set['size'] = dag.size()
          return dag

  nested = QuantumCircuit(3)
  nested.cx(0, 1); nested.cx(1, 2)
  nested.h(2); nested.h(2)
  nested.cx(1, 2); nested.cx(0, 1)

  state = {'prev': None}
  def not_converged(property_set):
      changed = property_set['size'] != state['prev']
      state['prev'] = property_set['size']
      return changed

  pm_loop = PassManager()
  pm_loop.append(DoWhileController(
      [InverseCancellation([CXGate(), HGate()]), RecordSize()],
      do_while=not_converged))
  looped = pm_loop.run(nested)
  print("one pass :", dict(PassManager([InverseCancellation([CXGate(), HGate()])])
                           .run(nested).count_ops()))
  print("to fixpoint:", dict(looped.count_ops()), "size", looped.size())
  print("same unitary?", Operator(looped).equiv(Operator(nested)))
  ```

  Real output:

  ```
  start      : {'cx': 4, 'h': 2}
  one pass   : {'cx': 4}
  to fixpoint: {}            -> size 0
  same unitary? True
  ```

  The circuit is a perfectly nested palindrome, so it is the identity — but a single
  `InverseCancellation` sweep only strips the innermost `h·h` pair. The loop then
  peels `cx(1,2)·cx(1,2)`, and finally `cx(0,1)·cx(0,1)`, reducing the circuit to
  nothing. Three iterations for three nesting levels.

  **Notes on the API and the idea.**

  - `DoWhileController` lives in `qiskit.passmanager`, not
    `qiskit.transpiler.passmanager`.
  - The `do_while` callable receives the `property_set` and must return a bool. Your
    convergence signal has to be *written into the property set by a pass* — a
    closure over a mutable `state` dict, as above, is the standard way to compare
    against the previous iteration.
  - Always bound the loop in production code (`DoWhileController` takes
    `options={'max_iteration': N}`, default 1000); a predicate that never settles
    will otherwise raise rather than spin forever.
  - This is exactly why the preset pass managers wrap their optimisation stage in a
    `DoWhileController` keyed on circuit depth and size.

  </details>

---

## Module 6 — Hardware-Aware Optimization

**Objective:** Use knowledge of hardware properties to make better transpilation decisions.

### Key Hardware Properties

| Property | Impact on Transpilation |
|---|---|
| Coupling map | Which qubit pairs can have 2Q gates |
| Gate error rates | Prefer high-fidelity qubit pairs |
| Gate durations | Minimize circuit duration for decoherence |
| T1, T2 times | Set maximum useful circuit depth |
| Readout error | Affects measurement fidelity |

### Backend Target API

The BackendV1 `backend.properties()` / `props.gate_error(...)` interface was removed with BackendV1 in Qiskit 2.0. Hardware characteristics now live on the `Target`:

```python
# Requires qiskit-ibm-runtime (fake backends live in its fake_provider)
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2

# FakeNairobiV2 snapshots the retired Nairobi device; its two-qubit
# basis gate is 'cx' (current Eagle/Heron devices use 'ecr'/'cz').
backend = FakeNairobiV2()
target = backend.target

# Error and duration for a specific gate instance
cx_props = target['cx'][(0, 1)]
print(cx_props.error, cx_props.duration)

# Readout error is the 'measure' instruction's error
meas_err_q0 = target['measure'][(0,)].error

# Enumerate all CX pairs and find the best one
best = min(target['cx'], key=lambda pair: target['cx'][pair].error)

# The coupling map is derived from the target
cm = target.build_coupling_map()

# Qubit coherence times
print(target.qubit_properties[0].t1, target.qubit_properties[0].t2)
```

### Noise-Aware Layout

```python
from qiskit.transpiler.passes import VF2PostLayout, SabreLayout

target_basis = ['cx', 'rz', 'sx', 'x']  # match the backend target's basis

# VF2PostLayout: after initial layout, try to improve using error rates
pm_noise_aware = PassManager([
    SabreLayout(coupling_map, max_iterations=5),
    VF2PostLayout(
        target=backend.target,
        max_trials=50,
        seed=42,
    ),
    SabreSwap(coupling_map, heuristic='decay'),
    BasisTranslator(sel, target_basis),
    Optimize1qGatesDecomposition(basis=target_basis),
])
```

### Dynamic Circuits (Feed-Forward)

QASM 3 + new IBM systems support mid-circuit measurement and real-time classical feed-forward:

```python
from qiskit.circuit import QuantumCircuit, IfElseOp

qc = QuantumCircuit(2, 1)
qc.h(0)
qc.measure(0, 0)
with qc.if_test((0, 1)):
    qc.x(1)  # Conditioned on measurement result
```

**Exercises:**
- Use `backend.target` to find the two-qubit pair with lowest CX error

  <details><summary>Solution</summary>

  ```python
  from qiskit_ibm_runtime.fake_provider import FakeNairobiV2

  backend = FakeNairobiV2()
  target = backend.target

  pairs = {pair: target['cx'][pair] for pair in target['cx']}
  for pair in sorted(pairs, key=lambda p: pairs[p].error):
      print(f"cx{pair}: error={pairs[pair].error:.5f} "
            f"duration={pairs[pair].duration * 1e9:.0f} ns")

  best = min(pairs, key=lambda p: pairs[p].error)
  worst = max(pairs, key=lambda p: pairs[p].error)
  print("best ", best, pairs[best].error)
  print("worst", worst, pairs[worst].error)
  ```

  Real output:

  ```
  cx(1, 3): error=0.00679  duration=270 ns
  cx(3, 1): error=0.00679  duration=306 ns
  cx(1, 2): error=0.00698  duration=427 ns
  cx(2, 1): error=0.00698  duration=391 ns
  cx(4, 5): error=0.00700  duration=313 ns
  cx(5, 4): error=0.00700  duration=277 ns
  cx(0, 1): error=0.00859  duration=249 ns
  cx(1, 0): error=0.00859  duration=284 ns
  cx(5, 6): error=0.01066  duration=341 ns
  cx(6, 5): error=0.01066  duration=306 ns
  cx(3, 5): error=0.01257  duration=640 ns
  cx(5, 3): error=0.01257  duration=604 ns
  best  = (1, 3)  0.00679
  worst = (3, 5)  0.01257   ratio 1.9x
  ```

  **What to read out of this.**

  - The spread is **1.9×** between best and worst pair on a 7-qubit device; on
    127-qubit Eagle devices the spread is routinely 10× or more, and a handful of
    pairs are effectively unusable. That spread is the entire justification for
    noise-aware layout.
  - Error is symmetric under direction reversal (`(1,3)` and `(3,1)` share a
    calibration) but **duration is not** — 270 ns versus 306 ns — because the
    hardware has one native direction and the other is the same pulse wrapped in
    single-qubit gates.
  - Duration and error are correlated but not proportional: `(3,5)` is both the
    slowest (640 ns) and the worst, but `(1,2)` at 427 ns beats `(0,1)` at 249 ns.

  The other two knobs on the same `Target`:

  ```python
  print({q: round(target['measure'][(q,)].error, 4) for q in range(7)})
  q0 = target.qubit_properties[0]
  print(round(q0.t1 * 1e6, 1), round(q0.t2 * 1e6, 1))
  ```

  ```
  {0: 0.058, 1: 0.0199, 2: 0.0193, 3: 0.0223, 4: 0.0183, 5: 0.0225, 6: 0.0258}
  89.1 15.8        # T1 / T2 of Q0, in microseconds
  ```

  `Q0` has a readout error three times everyone else's and a `T2` of 15.8 µs — avoid
  it for measured qubits even though its CX error looks acceptable. Note also
  `target.build_coupling_map()` for the connectivity, and that the BackendV1
  `backend.properties().gate_error(...)` interface is gone in Qiskit 2.0.

  </details>

- Re-transpile a circuit using noise-aware layout and measure fidelity improvement

  <details><summary>Solution</summary>

  To isolate the *layout* effect from the optimisation effect, hold the optimisation
  level fixed at 0 and vary only the starting qubits. Score with the expected
  fidelity from the previous exercise's error data.

  ```python
  from qiskit import QuantumCircuit, transpile
  from qiskit_ibm_runtime.fake_provider import FakeNairobiV2

  backend = FakeNairobiV2()
  target = backend.target

  def efid(isa):
      f = 1.0
      for inst in isa.data:
          if inst.operation.name in ('barrier', 'delay'):
              continue
          qargs = tuple(isa.find_bit(q).index for q in inst.qubits)
          props = target[inst.operation.name].get(qargs)
          if props is not None and props.error:
              f *= 1 - props.error
      return f

  deep = QuantumCircuit(2); deep.h(0)
  for _ in range(10):
      deep.cx(0, 1); deep.h(0); deep.t(1)
  deep.measure_all()

  for lay in ([3, 5], [0, 1], [1, 3]):
      t = transpile(deep, backend=backend, initial_layout=lay, optimization_level=0)
      print(lay, "cx =", t.count_ops()['cx'], " E[F] =", round(efid(t), 4))
  ```

  Real output:

  ```
  layout [3, 5]  (worst CX pair)  : cx=10  E[F]=0.8383
  layout [0, 1]                   : cx=10  E[F]=0.8432
  layout [1, 3]  (best CX pair)   : cx=10  E[F]=0.8921
  opt1 automatic layout [0, 1]    : cx=10  E[F]=0.8432
  ```

  Identical gate counts, **5.4 points of expected fidelity** purely from the choice
  of physical qubits — a 33% reduction in total expected error
  (`0.1617 → 0.1079`). Repeating the same scoring on the 5-qubit GHZ across
  optimisation levels and seeds gives `0.7716` at worst and `0.8519` at best, a 10%
  improvement.

  **Two honest caveats.**

  - The preset level-1 pipeline picked `[0, 1]` here, not the optimal `[1, 3]`: the
    trivial layout already satisfies the coupling map, so it is accepted and
    `VF2Layout`'s scoring — which looks at two-qubit gate error but not readout —
    does not override it. Do not assume the transpiler's layout is fidelity-optimal;
    score it yourself. `VF2PostLayout(target=..., max_trials=...)` exists precisely
    to re-examine the choice against error rates, and can be inspected via
    `pm.property_set['post_layout']`.
  - At `optimization_level ≥ 2` this comparison stops isolating layout at all:
    `ConsolidateBlocks` + KAK resynthesis collapse the ten-CX block to two, and the
    fidelity jumps to `0.95` for reasons that have nothing to do with which qubits
    were used. When benchmarking layout, freeze everything else.

  </details>

- Implement a dynamic circuit for quantum teleportation with mid-circuit measurement

  <details><summary>Solution</summary>

  Teleportation is the canonical dynamic circuit: two mid-circuit measurements feed
  forward into two conditional corrections. Build it with `if_test` on separate
  one-bit classical registers so each correction reads its own bit.

  ```python
  from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
  from qiskit_aer import AerSimulator

  q = QuantumRegister(3, 'q')
  c0 = ClassicalRegister(1, 'c0')   # Alice's q0 outcome  -> Z correction
  c1 = ClassicalRegister(1, 'c1')   # Alice's q1 outcome  -> X correction
  out = ClassicalRegister(1, 'out')
  tele = QuantumCircuit(q, c0, c1, out)

  theta, phi = 1.1, 0.7
  tele.ry(theta, 0); tele.rz(phi, 0)        # the state to teleport, on q0
  tele.barrier()
  tele.h(1); tele.cx(1, 2)                  # Bell pair shared by Alice and Bob
  tele.cx(0, 1); tele.h(0)                  # Bell-basis measurement
  tele.measure(0, c0); tele.measure(1, c1)
  with tele.if_test((c1, 1)):
      tele.x(2)
  with tele.if_test((c0, 1)):
      tele.z(2)
  tele.barrier()
  tele.rz(-phi, 2); tele.ry(-theta, 2)      # un-prepare: Bob must now hold |0>
  tele.measure(2, out)

  sim = AerSimulator()
  res = sim.run(transpile(tele, sim), shots=4096, seed_simulator=7).result()
  print(res.get_counts())
  ```

  Real output:

  ```
  raw counts (out c1 c0): {'0 0 1': 1019, '0 0 0': 996, '0 1 0': 1054, '0 1 1': 1027}
  marginal on 'out'     : {'0': 4096}   -> teleportation fidelity = 1.0
  ```

  Every shot measures `0` on the output bit, so the state arrived intact in all four
  Bell-measurement branches, which are (correctly) equiprobable at roughly 1024 each.

  **Points that matter in practice.**

  - **Verify by un-preparing.** Applying the inverse of the state-preparation on
    Bob's qubit and demanding a deterministic `0` is a far stronger test than
    eyeballing a Bloch sphere, and it works on hardware where you cannot read the
    statevector.
  - **Register layout is part of the design.** With a single 2-bit register you would
    have to condition on integer values (`if_test((creg, 0b01))`); separate one-bit
    registers make each correction independent and keep the conditions readable.
  - **Conditions are classical and ordered.** The `X` correction must be conditioned
    on the *second* qubit's outcome and the `Z` on the first; swapping them silently
    teleports the wrong state a quarter of the time.
  - **Hardware reality.** Feed-forward requires a backend whose target declares
    `if_else` (check `'if_else' in backend.operation_names`; FakeNairobiV2 does).
    The classical round trip costs hundreds of nanoseconds of extra idle time on the
    qubits, so dynamic circuits trade decoherence for the ability to branch — which
    is why deferred-measurement (replacing the conditionals with `CX`/`CZ`) is still
    preferred whenever the measurement is not needed mid-circuit.

  </details>

---

## Module 7 — Metrics and Benchmarking

**Objective:** Measure and compare transpilation quality objectively.

| Metric | Description |
|---|---|
| Gate count | Total number of gates |
| CX count | Two-qubit gate count (dominant cost) |
| Circuit depth | Longest path (critical path) |
| CX depth | Critical path counting only CX gates |
| T count | Relevant for fault-tolerant T-gate cost |
| SWAP overhead | Extra SWAPs inserted by router |
| Expected fidelity | `∏ (1 − ε_i)` over all gates — rough estimate |

```python
from qiskit.converters import circuit_to_dag

def circuit_metrics(qc):
    ops = qc.count_ops()
    return {
        'cx_count': ops.get('cx', 0),
        'depth': qc.depth(),
        'cx_depth': qc.depth(filter_function=lambda x: x.operation.name == 'cx'),
        'total_gates': sum(ops.values()),
    }
```

**Exercises:**
- Compare metrics for optimization levels 0, 1, 2, 3 on a 10-qubit random circuit

  <details><summary>Solution</summary>

  ```python
  import time
  from qiskit import transpile
  from qiskit.circuit.random import random_circuit
  from qiskit_ibm_runtime.fake_provider import FakeTorino

  def circuit_metrics(circ, two='cx'):
      ops = circ.count_ops()
      return {'2q': ops.get(two, 0), 'depth': circ.depth(),
              '2q_depth': circ.depth(filter_function=lambda x: x.operation.name == two),
              'total': sum(ops.values())}

  rand10 = random_circuit(10, 30, max_operands=2, seed=2024)
  backend = FakeTorino()          # Heron, CZ basis, 133 qubits
  for lvl in range(4):
      t0 = time.perf_counter()
      t = transpile(rand10, backend=backend, optimization_level=lvl, seed_transpiler=3)
      print(lvl, circuit_metrics(t, 'cz'), round(time.perf_counter() - t0, 2), "s")
  ```

  Real output (abstract circuit: depth 30, 271 gates, no two-qubit gates yet in the
  native basis):

  | level | CZ | depth | CZ-depth | total gates | compile time |
  |---|---|---|---|---|---|
  | 0 | 181 | 507 | 91 | 1539 | 0.14 s |
  | 1 | 109 | 237 | 71 | 598 | 0.05 s |
  | 2 | 88 | 167 | 48 | 506 | 0.05 s |
  | 3 | 81 | 183 | 50 | 485 | 0.03 s |

  **How to read this.**

  - The big win is `0 → 1`: two-qubit gates fall 40% and total gates 61%, because
    level 0 does no single-qubit merging at all and leaves every decomposition's
    scaffolding in place.
  - `1 → 2` buys another 19% of CZ and, more importantly, cuts **CZ-depth** from 71
    to 48. CZ-depth is the metric that tracks decoherence; total CZ count tracks
    incoherent gate error. They do not always move together.
  - `2 → 3` trades depth for count here (81 CZ but depth 183 versus 88 CZ at depth
    167). On a random circuit level 3 has little structure to exploit; on QFT,
    Trotter or ansatz circuits the gap is much larger.
  - Compile time is *not* monotonic in the level — level 3 was the fastest run here
    because it fed a smaller circuit into the later stages. Never assume "higher
    level = slower" without measuring.

  **Always report the metric you actually care about.** For a NISQ run, rank by
  expected fidelity (the last exercise in this module); for a fault-tolerant
  estimate, rank by T-count; for a coherence-limited device, rank by two-qubit
  depth. "Fewer gates" on its own is not a result.

  </details>

- Plot CX count vs optimization time for increasing circuit sizes

  <details><summary>Solution</summary>

  ```python
  import time
  import matplotlib.pyplot as plt
  from qiskit import transpile
  from qiskit.circuit.random import random_circuit
  from qiskit_ibm_runtime.fake_provider import FakeTorino

  backend = FakeTorino()
  sizes, cz0, cz3, t0s, t3s = [], [], [], [], []
  for n in (4, 8, 16, 32, 64):
      circ = random_circuit(n, n, max_operands=2, seed=n)
      row = {}
      for lvl in (0, 3):
          start = time.perf_counter()
          t = transpile(circ, backend=backend, optimization_level=lvl,
                        seed_transpiler=3)
          row[lvl] = (t.count_ops().get('cz', 0), time.perf_counter() - start)
      sizes.append(n)
      cz0.append(row[0][0]); cz3.append(row[3][0])
      t0s.append(row[0][1]); t3s.append(row[3][1])

  fig, ax = plt.subplots(1, 2, figsize=(9, 3.5))
  ax[0].loglog(sizes, cz0, 'o-', label='level 0')
  ax[0].loglog(sizes, cz3, 's-', label='level 3')
  ax[0].set_xlabel('qubits n'); ax[0].set_ylabel('CZ count'); ax[0].legend()
  ax[1].loglog(sizes, t0s, 'o-', label='level 0')
  ax[1].loglog(sizes, t3s, 's-', label='level 3')
  ax[1].set_xlabel('qubits n'); ax[1].set_ylabel('transpile time (s)'); ax[1].legend()
  fig.tight_layout()
  ```

  Real measurements (`random_circuit(n, n)`, depth equal to width, on FakeTorino):

  | n | L0 CZ | L0 time | L3 CZ | L3 time | CZ saved |
  |---|---|---|---|---|---|
  | 4 | 11 | 0.13 s | 5 | 0.01 s | 55% |
  | 8 | 156 | 0.01 s | 78 | 0.02 s | 50% |
  | 16 | 1 133 | 0.01 s | 535 | 0.04 s | 53% |
  | 32 | 5 601 | 0.02 s | 3 735 | 0.10 s | 33% |
  | 64 | 18 178 | 0.05 s | 13 969 | 0.67 s | 23% |

  **What the two curves say.**

  - **CZ count grows superlinearly** — roughly `n³` here, since the circuit has
    `O(n²)` two-qubit gates and routing on a fixed-degree lattice costs an extra
    `O(n^0.5)`–`O(n)` SWAP factor per gate. Level 0 to 64 qubits already needs 18 000
    CZ, far past what any NISQ device can execute.
  - **Compile time grows much faster at level 3 than level 0** — 0.01 s to 0.67 s,
    about `n^2.5`, dominated by `ConsolidateBlocks`/`UnitarySynthesis` (a KAK
    decomposition per two-qubit block) and the `DoWhileController` optimisation loop.
    Level 0 is nearly linear.
  - **The benefit of level 3 shrinks with size** — 55% fewer CZ at `n = 4`, only 23%
    at `n = 64` — because routing SWAPs, which optimisation cannot remove, become
    the dominant term. Optimisation fights gate redundancy; only a better layout or
    a better device topology fights routing overhead.

  The practical conclusion: for a large circuit you are usually better off spending
  the compile budget on *several level-1 or level-2 runs with different
  `seed_transpiler` values* and keeping the best, than on one level-3 run. Layout is
  stochastic, and the spread across seeds is often larger than the gap between
  levels.

  </details>

- Implement expected fidelity estimation using backend error rates

  <details><summary>Solution</summary>

  The estimator is a product over the calibrated instructions actually present in
  the ISA circuit — the two-qubit gates dominate, but readout and single-qubit
  errors are not negligible.

  ```python
  from qiskit import QuantumCircuit, transpile
  from qiskit_ibm_runtime.fake_provider import FakeNairobiV2

  def expected_fidelity(isa, target):
      """Product of (1 - error) over every calibrated instruction in an ISA circuit."""
      f, missing = 1.0, 0
      for inst in isa.data:
          name = inst.operation.name
          if name in ('barrier', 'delay'):
              continue
          qargs = tuple(isa.find_bit(q).index for q in inst.qubits)
          props = target[name].get(qargs) if name in target else None
          if props is None or props.error is None:
              missing += 1
              continue
          f *= 1.0 - props.error
      return f, missing

  backend = FakeNairobiV2()
  ghz5 = QuantumCircuit(5); ghz5.h(0)
  for i in range(4):
      ghz5.cx(0, i + 1)
  ghz5.measure_all()
  for lvl in range(4):
      isa = transpile(ghz5, backend=backend, optimization_level=lvl, seed_transpiler=7)
      f, miss = expected_fidelity(isa, backend.target)
      print(f"opt{lvl}: cx={isa.count_ops().get('cx', 0)} depth={isa.depth()} "
            f"E[F]={f:.4f} (uncalibrated skipped: {miss})")
  ```

  Real output:

  ```
  opt0: cx=13 depth=14 E[F]=0.7807 (uncalibrated skipped: 0)
  opt1: cx=7 depth=11 E[F]=0.8306 (uncalibrated skipped: 0)
  opt2: cx=5 depth=9 E[F]=0.8519 (uncalibrated skipped: 0)
  opt3: cx=5 depth=9 E[F]=0.8519 (uncalibrated skipped: 0)
  ```

  Transpiling well is worth 7 points of expected fidelity on a five-qubit GHZ — a
  **31% reduction in total expected error** (`0.2193 → 0.1481`) for zero extra
  hardware.

  **The model's four blind spots, which you must state whenever you quote a number
  like this.**

  - It assumes **independent, uncorrelated** errors. Real devices have crosstalk and
    correlated readout; the true fidelity is worse.
  - It ignores **idle decoherence**. A qubit waiting `t` while others compute decays
    at `exp(-t/T1)`; on the `T2 = 15.8 µs` qubits of this device a 5 µs idle is a
    sizeable error the product misses entirely. Add a `Delay`-aware term, or use
    scheduled circuits plus `T1`/`T2` from `target.qubit_properties`.
  - **`error` fields can be `None`** for instructions the backend does not
    characterise (`barrier`, `delay`, control flow). Count them, as above, rather
    than silently treating them as perfect — a fidelity of `1.0` with `missing = 40`
    is a bug, not good news.
  - It is a **worst-case-agnostic average**: it says nothing about which observable
    you are measuring. Two circuits with the same `E[F]` can give very different
    errors on `⟨ZZ⟩`.

  Use it to *rank* transpilations of the same circuit — which is what it is good at,
  and exactly what the preceding exercises did — not as a prediction of the fidelity
  you will measure.

  </details>

---

## Recommended Resources

| Resource | Type | Notes |
|---|---|---|
| Qiskit transpiler docs (docs.quantum.ibm.com/transpile) | Official docs | Primary reference |
| Amy et al. "Verified Compilation of Space-Efficient Reversible Circuits" | Paper | Gate synthesis theory |
| Cowtan et al. "On the Qubit Routing Problem" | Paper | Routing algorithm survey |
| Li et al. "Tackling the Qubit Mapping Problem for NISQ-Era Quantum Devices" | Paper | SABRE algorithm |
| Qiskit source — `qiskit/transpiler/passes/` | Source | Best way to learn the internals |

---

## Progression Checkpoints

- [ ] Manually decompose any single-qubit gate into {RZ, SX, X}

  <details><summary>Solution</summary>

  Every `U ∈ U(2)` is `e^(iα) RZ(φ) RY(θ) RZ(λ)` (ZYZ Euler). To reach `{RZ, SX, X}`,
  replace the `RY` using `RY(θ) = SX† RZ(θ) SX` up to phase, which after collecting
  the phases gives the standard five-gate form Qiskit emits:

  ```
  U  ≅  RZ(φ + 3π) · SX · RZ(θ + π) · SX · RZ(λ)        (circuit order: RZ(λ) first)
  ```

  Checked against a random unitary: `Operator(circ).equiv(U)` is `True`, with the
  angles taken straight from `OneQubitEulerDecomposer(basis='ZYZ').angles_and_phase`.
  Qiskit's own `OneQubitEulerDecomposer(basis='ZSX')` produces the same shape.

  Two special cases worth memorising:

  ```
  H = RZ(π/2) · SX · RZ(π/2)      (up to the global phase e^(-iπ/4))
  X = SX · SX,    S = RZ(π/2),    T = RZ(π/4),    Z = RZ(π)
  ```

  Three facts to be able to state:

  - **At most two `SX` gates** are ever needed; `RZ` is free on IBM hardware (a frame
    change in software, zero duration and zero error), so the *physical* cost of any
    single-qubit gate is one or two `SX` pulses.
  - That is why level-1 optimisation collapses long single-qubit runs so
    dramatically — an arbitrary chain becomes `RZ–SX–RZ–SX–RZ`.
  - The `X` in the basis set is there because `X = RZ(π)·SX·SX` up to phase is more
    expensive than a single calibrated `X` pulse.

  You can grade yourself by generating 100 random `2×2` unitaries, decomposing each
  by hand into the five-gate form, and asserting `Operator.equiv` on all of them.

  </details>

- [ ] Route a circuit onto a line topology by hand using SWAP insertion

  <details><summary>Solution</summary>

  The procedure, on a line `Q0 – Q1 – … – Q(n-1)`:

  1. Write down the interaction graph of the logical circuit (which qubit pairs share
     a two-qubit gate, and in what order).
  2. Choose an initial layout that puts the highest-degree logical qubit on the
     highest-degree physical qubit. On a line that means the *middle*.
  3. Walk the gate list. For each two-qubit gate whose physical qubits are `d` apart,
     insert `d - 1` SWAPs along the path, updating your logical→physical table after
     every SWAP.
  4. Do **not** restore the identity permutation at the end — record the final
     mapping and relabel classical bits at read-out. Restoring it roughly doubles the
     SWAP count.

  Worked example (from this lesson's Module 3 exercise): the CX triangle
  `CX(q0,q1); CX(q0,q2); CX(q1,q2)` on the line `Q0–Q1–Q2`. Trivial layout costs 2
  SWAPs; putting the hub `q0` on the middle qubit `Q1` costs 1. On the full Nairobi
  device, `optimization_level=3` gets it to 4 CX by also using the identity
  `CX(a,b) · SWAP(a,b) = CX(b,a) · CX(a,b)`, so a CNOT followed by a SWAP costs 2 CX
  rather than 4.

  Self-check: every two-qubit instruction's index pair must appear in
  `CouplingMap.from_line(n).get_edges()`, and `Operator.from_circuit(routed)` must
  equal `Operator(original)`.

  A useful mental benchmark: routing a GHZ star of `n` qubits onto a line needs
  `n - 2` SWAPs; routing a fully-connected `n`-qubit interaction graph onto a line
  needs `Θ(n²)` — which is why hardware topology, not gate count, sets the practical
  ceiling on circuit size.

  </details>

- [ ] Build a custom PassManager with routing + translation + optimization

  <details><summary>Solution</summary>

  A complete custom pipeline has four named stages and an assertion at the end:

  ```python
  from qiskit.transpiler import PassManager, CouplingMap
  from qiskit.transpiler.passes import (SabreLayout, BasisTranslator,
                                        Optimize1qGatesDecomposition,
                                        CommutativeCancellation, InverseCancellation)
  from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as sel
  from qiskit.circuit.library import CXGate

  basis = ['cx', 'rz', 'sx', 'x']
  pm = PassManager([
      SabreLayout(CouplingMap.from_line(5), max_iterations=3, seed=42),  # layout+routing
      BasisTranslator(sel, basis),                                       # translation
      Optimize1qGatesDecomposition(basis=basis),                         # optimisation
      InverseCancellation([CXGate()]),
      CommutativeCancellation(),
  ])
  ```

  What you should be able to justify:

  - **Order.** Layout and routing first (they insert SWAPs), translation second (it
    must see those SWAPs), optimisation last (it needs the final gate set to merge
    anything). Optimising before translation wastes work.
  - **`SabreLayout` routes.** No separate `ApplyLayout` or `SabreSwap` is required
    unless you pass `skip_routing=True`.
  - **Seeds.** `SabreLayout` is stochastic; fix `seed` for reproducibility, and in
    practice sweep several seeds and keep the best result by expected fidelity.
  - **Idempotence.** Single-pass cancellation is not a fixed point — wrap the
    optimisation passes in a `DoWhileController` if you want convergence.

  Verify with three assertions: every two-qubit pair lies on a coupling-map edge,
  every operation name is in `basis`, and
  `Operator.from_circuit(out).equiv(Operator(original))`.

  And know when *not* to do this: `generate_preset_pass_manager(optimization_level=k,
  backend=...)` is the production path and is what the runtime primitives expect. A
  hand-built pass manager is for research passes and for understanding the stages.

  </details>

- [ ] Write a custom TransformationPass that simplifies a specific pattern

  <details><summary>Solution</summary>

  A correct `TransformationPass` has a specific shape — this lesson's `RemoveDoubleX`
  is the template:

  ```python
  from qiskit.circuit.library import RZGate
  from qiskit.transpiler.basepasses import TransformationPass
  from qiskit.dagcircuit import DAGOpNode

  class MergeAdjacentRZ(TransformationPass):
      """Fuse RZ(a) · RZ(b) on the same qubit into RZ(a + b)."""

      def run(self, dag):
          merged = True
          while merged:
              merged = False
              for node in dag.topological_op_nodes():
                  if node.op.name != 'rz':
                      continue
                  for succ in dag.successors(node):
                      if (isinstance(succ, DAGOpNode) and succ.op.name == 'rz'
                              and succ.qargs == node.qargs):
                          total = node.op.params[0] + succ.op.params[0]
                          dag.substitute_node(succ, RZGate(total), inplace=True)
                          dag.remove_op_node(node)
                          merged = True
                          break
                  if merged:
                      break
          return dag
  ```

  The rules to internalise:

  1. **Never mutate the DAG while iterating it.** Either collect the edits first and
     apply them afterwards (the `RemoveDoubleX` style earlier in this module) or
     restart the iteration after each edit, as above.
  2. **Never remove the same node twice.** `remove_op_node` on a node already gone
     raises; keep a `matched` set, or restart.
  3. **Change a gate with `dag.substitute_node(node, NewGate(...), inplace=True)`**,
     not by assigning into `node.op.params`. Mutating an existing op's parameter list
     does not reliably propagate — a silent-wrong-answer bug that `Operator.equiv`
     catches and a gate count does not.
  4. **`dag.successors()` yields wire nodes too.** Filter with
     `isinstance(node, DAGOpNode)`; the old `node.type == 'op'` API is gone in
     Qiskit 2.0.
  5. **Successor is not the same as "next on this wire".** Two gates can be graph
     successors with another gate between them on a different qubit — check
     `succ.qargs == node.qargs` for single-qubit patterns, and every shared wire for
     multi-qubit patterns.
  6. **A `TransformationPass` returns the modified DAG; an `AnalysisPass` returns it
     unchanged and writes to `property_set`.** Mixing the two silently breaks
     `DoWhileController` predicates.

  Test it the way you would test any rewrite: build circuits that *do* match the
  pattern, circuits that *nearly* match (same gate, different qubit; interleaved
  third gate), assert `Operator` equivalence in every case, and check the gate count
  actually dropped where it should. For the pass above:
  `rz(0.3,0); rz(0.4,0); cx(0,1); rz(0.1,1); rz(0.2,1); rz(0.5,0)` goes from 5 `rz`
  to 3 — `Rz(0.7)` and `Rz(0.5)` on `q0`, `Rz(0.3)` on `q1` — with
  `Operator(before).equiv(Operator(after))` returning `True`.

  </details>

- [ ] Use noise-aware layout to improve expected circuit fidelity

  <details><summary>Solution</summary>

  The workflow, end to end:

  1. **Get the error data.** `target = backend.target`; `target['cx'][(i,j)].error`
     and `.duration`, `target['measure'][(q,)].error`,
     `target.qubit_properties[q].t1 / .t2`. (The BackendV1
     `backend.properties().gate_error(...)` path was removed in Qiskit 2.0.)
  2. **Define a score.** `E[F] = Π (1 - error)` over every calibrated instruction in
     the ISA circuit, counting the instructions you could not score rather than
     ignoring them.
  3. **Search.** Either let the preset pipeline do it (`VF2Layout` at level ≥ 1 scores
     candidate embeddings by error rate, `VF2PostLayout` re-examines the choice after
     routing) or sweep `seed_transpiler` and keep the best-scoring result.
  4. **Report the improvement honestly** — as a reduction in total expected *error*,
     not as a fidelity delta, and with the optimisation level held fixed so you are
     measuring layout rather than resynthesis.

  Measured on FakeNairobiV2 in this module's exercises: a two-qubit circuit pinned to
  the worst CX pair `(3,5)` scores `E[F] = 0.8383`; on the best pair `(1,3)` the same
  circuit scores `0.8921` — a 33% cut in expected error with identical gate counts.
  Across optimisation levels and seeds, a 5-qubit GHZ ranges from `0.7716` to
  `0.8519`.

  Two things a good answer also says:

  - The transpiler's automatic choice is not always optimal. At level 1 the trivial
    layout `[0, 1]` was kept because it already satisfies the coupling map, even
    though `[1, 3]` scores better — `VF2Layout`'s cost function weighs two-qubit gate
    error, not readout error, and `Q0` here has a `5.8%` readout error.
  - The product model ignores crosstalk, idle decoherence and correlated readout, so
    use it to *rank* candidates, not to predict the number you will measure.

  </details>

- [ ] Measure and compare transpilation quality across optimization levels

  <details><summary>Solution</summary>

  A defensible comparison has four ingredients.

  **1 — Metrics, plural.** At minimum: two-qubit gate count, two-qubit *depth*, total
  gate count, and expected fidelity. They do not move together — in this lesson's
  10-qubit benchmark, level 3 gave fewer CZ (81 vs 88) but *greater* depth (183 vs
  167) than level 2.

  **2 — The measurements.** On FakeTorino with a 10-qubit, depth-30 random circuit:

  | level | CZ | depth | CZ-depth | total | time |
  |---|---|---|---|---|---|
  | 0 | 181 | 507 | 91 | 1539 | 0.14 s |
  | 1 | 109 | 237 | 71 | 598 | 0.05 s |
  | 2 | 88 | 167 | 48 | 506 | 0.05 s |
  | 3 | 81 | 183 | 50 | 485 | 0.03 s |

  **3 — Control the randomness.** Layout is stochastic: always fix
  `seed_transpiler`, and report a *distribution* over several seeds rather than one
  number. On the GHZ benchmark the spread across three seeds at a single level was
  comparable to the gap between adjacent levels.

  **4 — Scale-dependence.** Level 3's advantage shrinks as circuits grow — 55% fewer
  CZ at 4 qubits, 23% at 64 — because routing SWAPs, which optimisation cannot
  remove, come to dominate. Meanwhile level-3 compile time grows far faster than
  level 0 (0.01 s to 0.67 s over the same range).

  The conclusion a good answer reaches: for small structured circuits use level 3;
  for large circuits spend the same wall-clock budget on multiple level-1 or level-2
  runs with different seeds and keep the best by expected fidelity.

  </details>

- [ ] Implement a dynamic circuit using mid-circuit measurement and feed-forward

  <details><summary>Solution</summary>

  You can check yourself against the teleportation circuit in Module 6: a Bell pair,
  a Bell-basis measurement with `measure` mid-circuit, and two `with qc.if_test(...)`
  blocks applying `X` and `Z` corrections — verified by un-preparing the state on the
  receiving qubit and measuring a deterministic `0` on all 4096 shots.

  The five things a complete answer demonstrates:

  - **Syntax.** `with qc.if_test((creg, value)):` (and `.else_()` on the returned
    context) is the Qiskit 2.x form. The old `gate.c_if(...)` API is removed.
  - **Register design.** Use one classical register per independent condition, so
    each branch reads its own bit rather than matching an integer pattern over a
    wider register.
  - **Backend support.** The target must declare `if_else` — check
    `'if_else' in backend.operation_names`. Dynamic circuits also require QASM 3 on
    the wire; QASM 2 cannot express them.
  - **Cost.** The classical round trip is hundreds of nanoseconds during which every
    qubit idles and decoheres. Compare against the deferred-measurement version
    (replace each conditional gate by a coherent controlled gate and measure at the
    end) and be able to say when each wins: deferred measurement costs qubits and
    coherent depth, feed-forward costs idle time and needs hardware support.
  - **Verification.** Measure a marginal that must be deterministic. Counting the
    four Bell-measurement branches at roughly `shots/4` each confirms the
    measurement is really mid-circuit and not deferred by the compiler.

  Natural follow-ons that use the same machinery: repeat-until-success gate
  synthesis, magic-state injection, and a single round of syndrome extraction with
  feed-forward correction on the three-qubit bit-flip code.

  </details>


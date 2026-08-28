# Quantum Parallelism and Interference

> **Prerequisites**: 03_quantum_gates_and_circuits/01_single_qubit_gates.md, 02_multi_qubit_gates.md, 02_quantum_mechanics/02_qubits_and_the_bloch_sphere.md  
> **Connects to**: All quantum algorithms — this chapter explains the conceptual mechanisms (parallelism, interference, phase kickback) that enable every quantum speedup

## Overview

"Quantum computers are faster because they can try all answers at once." This statement is popular and not entirely wrong — but it is dangerously incomplete. The real story requires understanding what quantum parallelism *actually* gives you, why you cannot simply "read off" all answers, and what mechanism actually produces quantum speedups.

Quantum parallelism is real: applying a function `f` to the uniform superposition `(1/√2^n)Σ|x⟩` evaluates `f` on all `2ⁿ` inputs with a single circuit application. But **measurement destroys the superposition** — you cannot extract more than `n` bits of classical information from an `n`-qubit measurement. Quantum algorithms do not work by "reading off" exponentially many results; they work by engineering interference patterns so that the correct answer has high measurement probability.

**Interference** is the true engine of quantum speedup. Amplitudes — complex numbers that evolve under unitary gates — can constructively reinforce (making desired outcomes more likely) or destructively cancel (making wrong answers improbable). Classical probability does not have this; probabilities only add, they never cancel. Quantum amplitudes can cancel because they are complex numbers, not non-negative reals.

**Phase kickback** is the mechanism by which a phase encoded in a quantum operation is transferred to a control register, making it manipulable. It underlies the Deutsch-Jozsa algorithm, Bernstein-Vazirani, quantum phase estimation, and Shor's algorithm.

Understanding these three concepts — parallelism, interference, phase kickback — is understanding why quantum algorithms work.

## Quantum Parallelism

### The Hadamard Transform Creates Superposition

Starting with `n` qubits in `|0⟩^n`, applying the `n`-qubit Hadamard `H^{⊗n}`:

$$H^{\otimes n}|0\rangle^n = \bigotimes_{k=1}^n H|0\rangle = \bigotimes_{k=1}^n \frac{|0\rangle+|1\rangle}{\sqrt{2}} = \frac{1}{\sqrt{2^n}}\sum_{x \in \{0,1\}^n} |x\rangle$$

This is the **uniform superposition** over all `2ⁿ` computational basis states. Each bit string appears with equal amplitude `1/√2ⁿ` and equal probability `1/2ⁿ`. With `n` gates (one H per qubit), we have created a state that "describes" all `2ⁿ` inputs simultaneously.

**Gate count**: `n` single-qubit gates, depth 1. Classically, writing down `2ⁿ` inputs takes `Θ(2ⁿ)` time.

### Evaluating a Function on All Inputs

Given a function `f: {0,1}ⁿ → {0,1}^m` implemented as a quantum oracle `O_f`:

$$O_f|x\rangle|0\rangle = |x\rangle|f(x)\rangle$$

Applying `O_f` to the uniform superposition:

$$O_f\left(\frac{1}{\sqrt{2^n}}\sum_x |x\rangle\right)|0\rangle = \frac{1}{\sqrt{2^n}}\sum_x |x\rangle|f(x)\rangle$$

With a **single application** of `O_f`, we have created a superposition of all input-output pairs! This is quantum parallelism. For a function requiring `T` gates to evaluate, we used just `T` gates to "evaluate" it on all `2ⁿ` inputs.

### Why You Cannot Read Off All Answers

Here is the catch: measuring the register collapses the superposition. If we measure the first `n` qubits (the input register), we get a uniformly random `x*` with probability `1/2ⁿ`, and the second register collapses to `|f(x*)⟩`. We learn `f(x*)` — one evaluation, chosen randomly. No better than a random classical evaluation.

**The information-theoretic barrier**: Holevo's bound says that `n` qubits can communicate at most `n` classical bits of information. A measurement of `n` qubits returns at most `n` classical bits. So from the `2ⁿ` computed values, we can extract at most `n` bits — an exponentially small fraction (`n/2ⁿ`) of what was "computed". Quantum parallelism does not overcome the measurement barrier.

**The right question to ask**: Instead of "what is `f(x*)`?" we need to ask questions whose answers are encoded in *global properties* of the function: "Is `f` constant or balanced?" (Deutsch-Jozsa), "What is the hidden period of `f`?" (Shor), "What is the location of the unique `x*` with `f(x*) = 1`?" (Grover). These global properties can be extracted with high probability using interference, even though individual values cannot.

## Interference

### Constructive and Destructive Interference

After creating a superposition and applying a function, we use quantum gates to **interfere** the amplitudes. This is the key step that most descriptions skip.

Consider the simple case of one qubit in `|+⟩ = (|0⟩+|1⟩)/√2` after applying `H`. Now apply `Z`:

$$Z|+\rangle = \frac{Z|0\rangle+Z|1\rangle}{\sqrt{2}} = \frac{|0\rangle-|1\rangle}{\sqrt{2}} = |-\rangle$$

Now apply `H` again:

$$H|-\rangle = H\frac{|0\rangle-|1\rangle}{\sqrt{2}} = \frac{H|0\rangle-H|1\rangle}{\sqrt{2}} = \frac{|+\rangle-|-\rangle}{\sqrt{2}} = \frac{(|0\rangle+|1\rangle)/\sqrt{2} - (|0\rangle-|1\rangle)/\sqrt{2}}{\sqrt{2}} = \frac{2|1\rangle/\sqrt{2}}{\sqrt{2}} = |1\rangle$$

The circuit `H·Z·H|+⟩` gives `|1⟩` with certainty. What happened?

- After `H`: both `|0⟩` and `|1⟩` have amplitude `1/√2`
- After `Z`: `|0⟩` amplitude unchanged (`+1/√2`), `|1⟩` amplitude negated (`-1/√2`)
- After `H`: the `|0⟩` component of the H output:
  - From `|0⟩`: `(1/√2) · (1/√2) = +1/2`
  - From `|1⟩`: `(-1/√2) · (1/√2) = -1/2` ← these cancel! **Destructive interference** at `|0⟩`
  - The `|1⟩` component:
  - From `|0⟩`: `(1/√2) · (1/√2) = +1/2`
  - From `|1⟩`: `(-1/√2) · (-1/√2) = +1/2` ← these add! **Constructive interference** at `|1⟩`

The circuit used interference to concentrate all amplitude on `|1⟩`. Indeed, the full sequence starting from `|0⟩` is `H·Z·H|0⟩ = X|0⟩ = |1⟩` (the identity `H·Z·H = X`): the phase flip applied between the two Hadamards was converted by interference into a deterministic, measurable bit flip.

### Interference as the Key Resource

The Deutsch-Jozsa algorithm (next chapter) applies this idea to `n` qubits: evaluate a constant or balanced function, then use the Hadamard transform to interfere all the amplitudes. If the function is constant, all amplitudes constructively interfere at `|0⟩^n`, giving outcome `0...0` with certainty. If balanced, destructive interference at `|0⟩^n` makes that outcome impossible.

The Grover algorithm uses an iterated interference procedure (oracle + diffusion) to gradually amplify the amplitude of the target state while suppressing all others.

Shor's algorithm uses the quantum Fourier transform — an efficient interference circuit — to extract the hidden period from a superposition of `2ⁿ` computed values.

**No classical analogue**: Classical probability distributions can only add probabilities (non-negative), so they can never cancel. Interference — destructive cancellation of complex amplitudes — is a purely quantum phenomenon. This is why quantum and classical random algorithms behave so differently.

## The Hadamard Transform and Walsh-Hadamard Transform

### The Full Transform

The `n`-qubit Hadamard transform `H^{⊗n}` maps:

$$H^{\otimes n}|x\rangle = \frac{1}{\sqrt{2^n}}\sum_{y \in \{0,1\}^n} (-1)^{x \cdot y}|y\rangle$$

where `x·y = Σᵢ xᵢyᵢ mod 2` is the bitwise dot product. Each basis state `|x⟩` becomes a superposition where the amplitude of `|y⟩` depends on the parity of the bitwise overlap between `x` and `y`.

**Proof** (for one qubit): `H|0⟩ = (|0⟩+|1⟩)/√2 = (1/√2)Σ_y (-1)^{0·y}|y⟩` ✓, `H|1⟩ = (|0⟩-|1⟩)/√2 = (1/√2)Σ_y(-1)^{1·y}|y⟩` ✓. For `n` qubits, the tensor product multiplies the amplitudes, so `x·y = Σᵢxᵢyᵢ mod 2` is the exponent.

**Self-inverse**: `(H^{⊗n})² = I` (applying the transform twice returns to the start).

**Classical analogy**: The Walsh-Hadamard transform (WHT) is the classical fast algorithm performing the same computation on classical amplitude arrays. It requires `O(n · 2ⁿ)` operations classically (via the fast Walsh-Hadamard algorithm, analogous to FFT). Quantum: `n` H gates, depth 1, `O(n)` gates. This is the **quantum exponential speedup** for computing the WHT itself — though this speedup is difficult to exploit for practical problems because the output is a quantum state, not a classical array.

### Action on Superpositions

For any state `|s⟩ = Σ_x α_x|x⟩`:

$$H^{\otimes n}|s\rangle = \sum_y \hat{\alpha}_y |y\rangle, \quad \hat{\alpha}_y = \frac{1}{\sqrt{2^n}}\sum_x (-1)^{x\cdot y}\alpha_x$$

This is the **Walsh-Hadamard transform** of the amplitude vector `{α_x}`. It is an orthogonal transform (over the reals if all amplitudes are real) and is its own inverse.

**Key identity for algorithms**: For `|s⟩ = |x⟩` (a specific computational basis state):

$$H^{\otimes n}|x\rangle = \frac{1}{\sqrt{2^n}}\sum_y (-1)^{x\cdot y}|y\rangle$$

The phases `(-1)^{x·y}` encode the value of `x` in the Fourier domain. The Bernstein-Vazirani algorithm reads these phases directly.

## Phase Kickback

### Mechanism

Phase kickback is the mechanism by which a phase acquired by the target qubit of a controlled operation is transferred ("kicked back") to the control qubit.

**Basic phase kickback**: Given a unitary `U` with eigenvector `|u⟩` and eigenvalue `e^{iφ}`:

$$U|u\rangle = e^{i\varphi}|u\rangle$$

The controlled-`U` gate with control `|+⟩ = (|0⟩+|1⟩)/√2` and target `|u⟩`:

$$(CU)\frac{|0\rangle+|1\rangle}{\sqrt{2}}|u\rangle = \frac{|0\rangle|u\rangle + |1\rangle U|u\rangle}{\sqrt{2}} = \frac{|0\rangle|u\rangle + e^{i\varphi}|1\rangle|u\rangle}{\sqrt{2}} = \frac{|0\rangle + e^{i\varphi}|1\rangle}{\sqrt{2}} \cdot |u\rangle$$

The target `|u⟩` is **unchanged** (it was an eigenstate). The phase `e^{iφ}` appears on the `|1⟩` component of the control qubit. This is phase kickback.

After kickback, the control qubit is in `(|0⟩ + e^{iφ}|1⟩)/√2`, which is a state encoding the phase `φ` in the relative phase between `|0⟩` and `|1⟩`. Applying `H` to the control converts this relative phase into a measurable amplitude difference.

### Why Phase Kickback Works

The key insight: the phase `e^{iφ}` is a **property of the eigenstate** `|u⟩` under `U`, but through the controlled operation it is "copied" to the control qubit without disturbing the eigenstate. The target qubit acts as a phase reference; the control qubit accumulates the phase information.

This is fundamentally different from classical conditional operations, where the control bit must be read to determine whether to apply the operation. In quantum mechanics, the operation runs "in superposition," and the phase appears on the control qubit rather than requiring any measurement.

### Phase Kickback in Algorithms

**Deutsch's algorithm**: `O_f|x⟩|−⟩ = (-1)^{f(x)}|x⟩|−⟩`. The `|−⟩` target "absorbs" the XOR and kicks back a phase `(-1)^{f(x)}` to the input register.

**Grover oracle**: `O_f|x⟩ = (-1)^{f(x)}|x⟩`. For the target item `x*`, the phase `-1` is kicked back onto `|x*⟩`, marking it with a phase flip.

**Phase estimation**: Controlled-`U^{2^k}` gates kick back the phase `e^{2πiφ · 2^k}` to ancilla qubits, building up a binary representation of `φ`. The inverse QFT then decodes this phase.

### General Phase Kickback Identity

For oracle `O_f|x⟩|b⟩ = |x⟩|b⊕f(x)⟩` with target in `|−⟩ = (|0⟩-|1⟩)/√2`:

$$O_f|x\rangle|-\rangle = |x\rangle(|0\oplus f(x)\rangle - |1\oplus f(x)\rangle)/\sqrt{2}$$

If `f(x) = 0`: `|x⟩(|0⟩-|1⟩)/√2 = |x⟩|−⟩` — no change.
If `f(x) = 1`: `|x⟩(|1⟩-|0⟩)/√2 = -|x⟩|−⟩` — phase flip on `|x⟩`.

Combined: `O_f|x⟩|−⟩ = (-1)^{f(x)}|x⟩|−⟩`.

The target `|−⟩` is unchanged; the phase `(-1)^{f(x)}` appears on the input register. This converts a **bit oracle** `O_f` (XOR form) into a **phase oracle** (phase flip form) — a crucial transformation used in every quantum algorithm that uses an oracle.

## Key Formulas

**Uniform superposition**:
$$H^{\otimes n}|0\rangle^n = \frac{1}{\sqrt{2^n}}\sum_{x \in \{0,1\}^n}|x\rangle$$

**Quantum parallelism (function evaluation)**:
$$O_f\left(\frac{1}{\sqrt{2^n}}\sum_x|x\rangle\right)|0\rangle = \frac{1}{\sqrt{2^n}}\sum_x|x\rangle|f(x)\rangle$$

**Hadamard transform on basis state**:
$$H^{\otimes n}|x\rangle = \frac{1}{\sqrt{2^n}}\sum_y(-1)^{x\cdot y}|y\rangle$$

**Phase kickback**:
$$(CU)|+\rangle|u\rangle = \frac{|0\rangle + e^{i\varphi}|1\rangle}{\sqrt{2}}|u\rangle \quad \text{when } U|u\rangle = e^{i\varphi}|u\rangle$$

**Phase oracle from bit oracle**:
$$O_f|x\rangle|-\rangle = (-1)^{f(x)}|x\rangle|-\rangle$$

## Worked Example

**Problem**: Consider `n = 2` qubits. Starting from `|00⟩`, apply `H⊗H`, then apply the oracle `O_f` for the constant function `f(x) = 1` (i.e., `f(00) = f(01) = f(10) = f(11) = 1`). Use a third ancilla qubit in `|−⟩`. Then apply `H⊗H` to the first two qubits. What is the final state of the first two qubits? What probability do we get outcome `00`?

**Solution**:

Step 1 — After `H⊗H`:

$$H^{\otimes 2}|00\rangle = |+\rangle|+\rangle = \frac{1}{2}(|00\rangle+|01\rangle+|10\rangle+|11\rangle)$$

Step 2 — Apply oracle with `|−⟩` ancilla:

Using phase kickback: since `f(x) = 1` for all `x`:
$$O_f|x\rangle|-\rangle = (-1)^{f(x)}|x\rangle|-\rangle = (-1)^1|x\rangle|-\rangle = -|x\rangle|-\rangle$$

The ancilla `|−⟩` is unchanged. The first two qubits:
$$-\frac{1}{2}(|00\rangle+|01\rangle+|10\rangle+|11\rangle)$$

The global phase `-1` is unobservable.

Step 3 — Apply `H⊗H`:

Using `H^{⊗n}|x⟩ = (1/√2ⁿ)Σ_y (-1)^{x·y}|y⟩`:

$$H^{\otimes 2}\left[\frac{1}{2}\sum_x|x\rangle\right] = \frac{1}{2}\sum_x H^{\otimes 2}|x\rangle = \frac{1}{2}\sum_x \frac{1}{2}\sum_y(-1)^{x\cdot y}|y\rangle$$

$$= \frac{1}{4}\sum_y |y\rangle \sum_x (-1)^{x\cdot y}$$

The inner sum `Σ_x (-1)^{x·y}`:
- For `y = 00`: `(-1)^{0+0} + (-1)^{0+0} + (-1)^{0+0} + (-1)^{0+0} = 4` (all same phase, all `+1`)
- For `y = 01`: `(-1)^0 + (-1)^1 + (-1)^0 + (-1)^1 = 1-1+1-1 = 0` (alternating, cancel)
- For `y = 10`: `(-1)^0 + (-1)^0 + (-1)^1 + (-1)^1 = 1+1-1-1 = 0` (cancel)
- For `y = 11`: `(-1)^0 + (-1)^1 + (-1)^1 + (-1)^{1+1} = 1-1-1+1 = 0` (cancel)

So:
$$H^{\otimes 2}\left[\frac{1}{2}\sum_x|x\rangle\right] = \frac{1}{4}\cdot 4 \cdot |00\rangle = |00\rangle$$

The outcome is `|00⟩` with **probability 1**. This is Deutsch-Jozsa for `f = const`: the constant function always gives outcome `00...0`.

**Interference at work**: All four inputs had amplitude `+1/2` after the (trivially-phased, since `f=1` adds global `-1`) oracle step. The Hadamard `H^{⊗2}` then constructively interfered all amplitudes to concentrate at `|00⟩`. The outcome is certain.

**Contrast**: If `f` had been balanced (two inputs giving 0, two giving 1), the phases would be mixed (`+1/2` and `-1/2`), causing destructive interference at `|00⟩` and constructive interference elsewhere. The probability of outcome `00` would be exactly 0.

This perfect separation — certain outcome `00` for constant, impossible for balanced — is the Deutsch-Jozsa effect, requiring only 1 quantum query versus 2^{n-1}+1 classical queries.

## Summary

- **Quantum parallelism**: applying `O_f` to the uniform superposition evaluates `f` on all `2ⁿ` inputs simultaneously with a single oracle call; but measurement yields only one output
- **Interference** — constructive reinforcement and destructive cancellation of complex amplitudes — is the mechanism that makes quantum algorithms outperform classical; it has no classical analogue (probabilities cannot cancel)
- The **Hadamard transform** `H^{⊗n}` implements a Walsh-Hadamard transform in depth 1 with `n` gates; classical WHT costs `O(n · 2ⁿ)` operations
- **Phase kickback**: when a controlled-U is applied with target in an eigenstate `|u⟩`, the phase `e^{iφ}` appears on the control qubit; the target is unchanged; this is the core mechanism of Deutsch-Jozsa, QPE, and Shor
- Phase oracle from bit oracle: `O_f|x⟩|−⟩ = (-1)^{f(x)}|x⟩|−⟩` — preparing the ancilla in `|−⟩` converts XOR into a phase flip
- Quantum speedups require choosing problems where the **answer** is a global property of `f` that can be extracted via interference, not just one value of `f`

## Exercises

**Exercise 1**: Compute `H^{⊗2}|11⟩` explicitly using the formula `H^{⊗n}|x⟩ = (1/√2ⁿ)Σ_y (-1)^{x·y}|y⟩`. Which outcomes interfere destructively if this state is superposed with `H^{⊗2}|00⟩`?

<details><summary>Solution</summary>

With `x = 11`, the phase of `|y⟩` is `(-1)^{y₁+y₂}`:

`H^{⊗2}|11⟩ = (1/2)(|00⟩ - |01⟩ - |10⟩ + |11⟩)`

Since `H^{⊗2}|00⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)`, the (normalized) sum of the two output states is

`(1/√2)(H^{⊗2}|00⟩ + H^{⊗2}|11⟩) = (1/√2)(|00⟩ + |11⟩)`

The `|01⟩` and `|10⟩` components cancel — destructive interference — while `|00⟩` and `|11⟩` reinforce. (Equivalently: `H^{⊗2}` applied to the Bell-like input `(|00⟩+|11⟩)/√2` returns a state supported only on even-parity strings.)

</details>

**Exercise 2**: Phase kickback with the `T` gate: apply controlled-`T` with control in `|+⟩` and target in `|1⟩` (an eigenstate of `T` with eigenvalue `e^{iπ/4}`). What is the control-qubit state afterward, and with what probability does a subsequent measurement of the control in the `{|+⟩, |−⟩}` basis give `|+⟩`?

<details><summary>Solution</summary>

Phase kickback leaves the target `|1⟩` unchanged and puts the control in

`(|0⟩ + e^{iπ/4}|1⟩)/√2`

Probability of `|+⟩`: `|⟨+|ψ⟩|² = |(1 + e^{iπ/4})/2|² = (1 + cos(π/4))/2 = cos²(π/8) ≈ 0.854`.

(General rule: `P(+) = (1 + cos φ)/2 = cos²(φ/2)` for kicked-back phase `e^{iφ}` — the basis of the Hadamard test for estimating eigenphases.)

</details>

**Exercise 3**: Run the `n = 2` interference circuit of the worked example, but with the *balanced* function `f(x₁x₂) = x₁` instead of a constant function. What is the final state of the input register, and what is the probability of outcome `00`?

<details><summary>Solution</summary>

After `H^{⊗2}` and the phase oracle: `(1/2)Σ_x (-1)^{x₁}|x⟩ = (1/2)(|00⟩ + |01⟩ - |10⟩ - |11⟩)`.

Note `(-1)^{x₁} = (-1)^{s·x}` with `s = 10`, so by the Bernstein-Vazirani identity the final `H^{⊗2}` maps this state exactly to `|s⟩ = |10⟩`.

Check via the amplitude formula: `amp(00) = (1/4)Σ_x (-1)^{f(x)} = (1/4)(1 + 1 - 1 - 1) = 0`.

Final state: `|10⟩`; probability of `00` is exactly `0` — perfect destructive interference at `|00⟩`, as required for a balanced function.

</details>

**Exercise 4**: A quantum circuit applies one oracle call for `f: {0,1}²⁰ → {0,1}` to the uniform superposition, "evaluating" `f` on all `2²⁰ ≈ 10⁶` inputs. (a) What is the maximum number of classical bits extractable by measuring the 21 qubits? (b) What fraction of the million computed function values is that? (c) Reconcile this with the fact that Deutsch-Jozsa still extracts something useful in one query.

<details><summary>Solution</summary>

(a) By Holevo's bound, at most 21 bits (one per qubit measured).

(b) `21/2²⁰ ≈ 2 × 10⁻⁵` — a vanishing fraction of the `~10⁶` computed bits.

(c) There is no contradiction: Deutsch-Jozsa does not read out function values. It asks a **one-bit global question** ("constant or balanced?") whose answer is encoded in the interference pattern of all `2²⁰` amplitudes simultaneously. Interference concentrates that single bit into a high-probability measurement outcome. Quantum advantage comes from converting global properties into measurable interference, never from reading out the parallel evaluations.

</details>

## Further Reading

1. **Nielsen & Chuang**, §1.4.3 (quantum parallelism) and §1.4.4 (Deutsch's algorithm) — introduces these ideas from scratch with the physical motivation
2. **Mosca**, "Quantum Algorithms" (arXiv:0808.0369) — comprehensive survey of quantum algorithms with emphasis on the unifying principles; explains interference as the core mechanism
3. **Cleve, Ekert, Macchiavello & Mosca**, "Quantum Algorithms Revisited" (Proceedings of the Royal Society A, 1998) — reframes early quantum algorithms in terms of phase kickback; the paper that clarified why these algorithms work
4. **Aaronson**, *Quantum Computing Since Democritus*, Chapter 9 — explains with great clarity why quantum computers are not "trying all answers at once" and what they actually do instead
5. **Feynman**, "Simulating Physics with Computers" (International Journal of Theoretical Physics, 1982) — the visionary paper that first proposed quantum computing based on the difficulty of simulating quantum interference classically

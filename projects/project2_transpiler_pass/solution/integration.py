"""integration.py -- milestone 3: putting the pass inside a real pipeline.

What ``generate_preset_pass_manager`` actually returns
-----------------------------------------------------
A ``StagedPassManager`` whose ``.stages`` attribute is, in Qiskit 2.5.2::

    ('init', 'layout', 'routing', 'translation', 'optimization', 'scheduling')

Each stage is a plain ``PassManager`` (or ``None``), and ``+=`` appends to one::

    pm.optimization += PassManager([CXRZCXFuser(), DropIdentityRZ()])

Placement matters and the two useful choices pull in opposite directions:

``init``          runs before layout, routing and translation, so the circuit is
                  still in its original basis (``cx`` even for a ``cz`` device)
                  and still on virtual qubits.  Fusing here removes 2-qubit
                  gates *before* routing has to find SWAPs for them.
``optimization``  runs last, after translation, so on a ``cz`` backend such as
                  FakeTorino there are no ``cx`` nodes left and this pass is a
                  no-op.  On a ``cx`` backend (FakeManilaV2) it sees the
                  translated circuit and can still act.
"""

from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.transpiler import PassManager, StagedPassManager, generate_preset_pass_manager

from passes import CXRZCXFuser, DropIdentityRZ

TWO_QUBIT_NAMES = ("cx", "cz", "ecr", "swap", "rzz")


def fuser_stage() -> PassManager:
    """The pass pair as a drop-in stage."""
    return PassManager([CXRZCXFuser(), DropIdentityRZ()])


def with_fuser(pm: StagedPassManager, stage: str = "optimization") -> StagedPassManager:
    """Append the fuser stage to ``stage`` of an existing preset pass manager."""
    if stage not in pm.stages:
        raise ValueError(f"{stage!r} is not one of {pm.stages}")
    existing = getattr(pm, stage)
    # GOTCHA: a stage can be None -- at optimization_level=0 the whole
    # ``optimization`` stage is absent, and ``None + PassManager`` raises
    # TypeError.  The docs show ``pm.optimization += ...`` with no caveat.
    setattr(pm, stage, fuser_stage() if existing is None else existing + fuser_stage())
    return pm


def count_2q(qc: QuantumCircuit) -> int:
    return sum(n for g, n in qc.count_ops().items() if g in TWO_QUBIT_NAMES)


def respects_coupling(qc: QuantumCircuit, backend) -> bool:
    """Every 2-qubit instruction sits on an edge of the backend's coupling map."""
    cmap = backend.target.build_coupling_map()
    if cmap is None:
        return True
    edges = {tuple(sorted(e)) for e in cmap.get_edges()}
    for inst in qc.data:
        qubits = [q for q in inst.qubits]
        if len(qubits) != 2:
            continue
        pair = tuple(sorted(qc.find_bit(q).index for q in qubits))
        if pair not in edges:
            return False
    return True


def is_isa_valid(qc: QuantumCircuit, backend) -> bool:
    """The backend's Target accepts every instruction in the circuit."""
    target = backend.target
    for inst in qc.data:
        name = inst.operation.name
        if name in ("barrier", "measure", "delay", "reset"):
            continue
        if not target.instruction_supported(name):
            return False
    return True


def bell_phase_circuit(blocks: int = 3, parameterised: bool = False) -> QuantumCircuit:
    """Bell state followed by ``blocks`` fusable CX-RZ-CX windows."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    for i in range(blocks):
        qc.cx(0, 1)
        qc.rz(Parameter(f"t{i}") if parameterised else 0.2 + 0.1 * i, 1)
        qc.cx(0, 1)
    return qc


def compare(backend, level: int, stage: str = "optimization",
            parameterised: bool = False, blocks: int = 3, seed: int = 7) -> dict:
    """Transpile the test circuit with and without the stage and measure."""
    qc = bell_phase_circuit(blocks, parameterised)
    base = generate_preset_pass_manager(optimization_level=level, backend=backend,
                                        seed_transpiler=seed)
    mine = with_fuser(generate_preset_pass_manager(
        optimization_level=level, backend=backend, seed_transpiler=seed), stage)
    a, b = base.run(qc), mine.run(qc)
    return {
        "backend": backend.name, "level": level, "stage": stage,
        "parameterised": parameterised,
        "twoq_without": count_2q(a), "twoq_with": count_2q(b),
        "rz_without": a.count_ops().get("rz", 0), "rz_with": b.count_ops().get("rz", 0),
        "depth_without": a.depth(), "depth_with": b.depth(),
        "isa_valid": is_isa_valid(b, backend),
        "coupling_ok": respects_coupling(b, backend),
    }

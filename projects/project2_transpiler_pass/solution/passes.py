"""passes.py -- milestones 1 and 2: two peephole TransformationPasses.

    DropIdentityRZ   removes RZ rotations that are the identity
    CXRZCXFuser      collapses  CX(c,t) . RZ(theta,t) . CX(c,t)  windows

The rewrite identity
--------------------
Write the CX with control c and target t.  Conjugating Z_t by that CX gives
Z_c Z_t, so

    CX . RZ(theta)_t . CX
        = CX . exp(-i theta Z_t / 2) . CX
        = exp(-i theta (CX Z_t CX) / 2)
        = exp(-i theta Z_c Z_t / 2)
        = RZZ(theta)

which is diagonal, so two adjacent blocks simply add their angles:

    RZZ(theta_1) . RZZ(theta_2) = RZZ(theta_1 + theta_2)

and a block with theta = 0 is the identity.  SOLUTION.md multiplies the 4x4
matrices out explicitly; ``test_passes.py::test_cx_rz_cx_is_rzz`` checks the
identity numerically for a grid of angles.

Global-phase convention (the milestone-1 decision)
--------------------------------------------------
RZ(theta) = diag(e^{-i theta/2}, e^{+i theta/2}), so

    RZ(2 pi k) = (-1)^k I

RZ(4 pi) is *exactly* the identity and can always be deleted.  RZ(2 pi) is
-I: as a standalone gate it is unobservable, but inside a controlled block it
is a relative phase and deleting it silently is a bug.  This implementation
therefore deletes every RZ whose angle is a multiple of 2 pi and *pays the
phase back* with ``dag.global_phase += theta / 2``, so the rewritten circuit
equals the original as an operator, not merely up to phase.  Constructing the
pass with ``track_global_phase=False`` switches to the conservative rule:
only multiples of 4 pi are removed and RZ(2 pi) is left alone.
"""

from __future__ import annotations

import math

from qiskit.circuit import ParameterExpression, Qubit
from qiskit.circuit.library import RZGate
from qiskit.dagcircuit import DAGCircuit, DAGOpNode
from qiskit.transpiler.basepasses import TransformationPass

TWO_PI = 2.0 * math.pi
FOUR_PI = 4.0 * math.pi


def _bound_angle(node: DAGOpNode) -> float | None:
    """The node's rotation angle as a float, or None if it is symbolic.

    TRAP: an unbound ``Parameter`` reaches here as a ``ParameterExpression``
    and ``float()`` on it raises ``TypeError``.  A pass that does not guard
    for this crashes the moment someone transpiles a parameterised ansatz --
    which is most of variational computing.
    """
    if not node.op.params:
        return None
    p = node.op.params[0]
    if isinstance(p, ParameterExpression) and p.parameters:
        return None
    try:
        return float(p)
    except (TypeError, ValueError):
        return None


def _raw_angle(node: DAGOpNode):
    """The node's angle as-is: a float, a symbolic ParameterExpression, or None."""
    return node.op.params[0] if node.op.params else None


def _is_multiple_of(theta: float, period: float, tol: float) -> bool:
    return abs(theta - period * round(theta / period)) <= tol


class DropIdentityRZ(TransformationPass):
    """Remove RZ gates that act as the identity (milestone 1).

    Parameters
    ----------
    tol
        Absolute tolerance on the angle, in radians.
    track_global_phase
        ``True`` (default): delete every multiple of 2 pi and compensate the
        DAG's global phase, so the operator is preserved exactly.
        ``False``: only multiples of 4 pi are deleted; RZ(2 pi) survives.
    """

    def __init__(self, tol: float = 1e-12, track_global_phase: bool = True) -> None:
        super().__init__()
        self.tol = tol
        self.track_global_phase = track_global_phase

    def run(self, dag: DAGCircuit) -> DAGCircuit:
        period = TWO_PI if self.track_global_phase else FOUR_PI
        for node in list(dag.op_nodes()):
            if node.op.name != "rz":
                continue
            if getattr(node.op, "condition", None) is not None:
                continue                      # never touch a classically conditioned gate
            theta = _bound_angle(node)
            if theta is None:                 # unbound Parameter -- leave alone
                continue
            if not _is_multiple_of(theta, period, self.tol):
                continue
            if self.track_global_phase:
                dag.global_phase += theta / 2.0
            dag.remove_op_node(node)
        return dag


class CXRZCXFuser(TransformationPass):
    """Collapse ``CX . RZ . CX`` windows (milestone 2).

    Two rewrites, applied to a fixed point:

    * **annihilate** -- a window whose angle is a multiple of 2 pi is the
      identity (up to the tracked global phase); all three gates go.
    * **fuse** -- two windows on the same qubit pair whose inner CXs are
      adjacent on *both* wires become one window with the summed angle,
      because the inner ``CX . CX`` is the identity.

    Both rewrites require the window to be *clean*: between the two CXs there
    must be nothing at all on the control wire, and nothing but the RZ on the
    target wire.  Those two checks are what the milestone's traps are about.
    """

    def __init__(self, tol: float = 1e-12, track_global_phase: bool = True,
                 max_sweeps: int = 64) -> None:
        super().__init__()
        self.tol = tol
        self.track_global_phase = track_global_phase
        self.max_sweeps = max_sweeps
        # populated by run(), handy for the benchmark
        self.stats = {"annihilated": 0, "fused": 0, "sweeps": 0}

    # -- wire bookkeeping ---------------------------------------------------
    #
    # TRAP that costs an hour if you miss it: in Qiskit 2.x the DAG lives in
    # Rust and ``dag.topological_op_nodes()`` hands out a *fresh* Python
    # ``DAGOpNode`` wrapper every time.  ``id(node)`` therefore differs
    # between two traversals of the same DAG, and ``==`` compares gate/qargs
    # semantically, so two identical CX gates on the same wires compare equal.
    # Neither can index a node.  ``node._node_id`` (the rustworkx index) is
    # the only stable handle; it is private, so it is isolated in ``_key``.

    @staticmethod
    def _key(node: DAGOpNode) -> int:
        return node._node_id

    @classmethod
    def _wire_order(cls, dag: DAGCircuit):
        """(per-qubit op order, node-position index).

        Restricting a topological order to one wire gives that wire's
        execution order, because every pair of ops sharing a qubit is
        connected in the DAG.
        """
        order: dict[Qubit, list[DAGOpNode]] = {q: [] for q in dag.qubits}
        pos: dict[tuple[int, Qubit], int] = {}
        for node in dag.topological_op_nodes():
            for q in node.qargs:
                pos[(cls._key(node), q)] = len(order[q])
                order[q].append(node)
        return order, pos

    @classmethod
    def _succ(cls, order, pos, node: DAGOpNode, wire: Qubit) -> DAGOpNode | None:
        """The next op on ``wire`` after ``node``, or None at the wire's end."""
        seq = order[wire]
        i = pos[(cls._key(node), wire)]
        return seq[i + 1] if i + 1 < len(seq) else None

    def _windows(self, dag: DAGCircuit):
        """Every clean ``CX, RZ, CX`` triple, in circuit order."""
        order, pos = self._wire_order(dag)
        found = []
        for node in dag.topological_op_nodes():
            if node.op.name != "cx" or len(node.qargs) != 2:
                continue
            ctrl, targ = node.qargs
            # target wire: the RZ must come next, then the closing CX
            rz = self._succ(order, pos, node, targ)
            # ... and the same identity trap applies to Qubit objects: use ==,
            # never `is`.  `is` silently matches nothing and the pass becomes
            # a very convincing no-op.
            if rz is None or rz.op.name != "rz" or rz.qargs[0] != targ:
                continue
            close = self._succ(order, pos, rz, targ)
            if close is None or close.op.name != "cx":
                continue
            # DIRECTION TRAP: cx(0,1) ... cx(1,0) is *not* a fusable window --
            # the second CX conjugates Z_t into Z_c Z_t the other way round.
            if tuple(close.qargs) != (ctrl, targ):
                continue
            # INTERLEAVED-WIRE TRAP: the control wire must be empty between the
            # two CXs, i.e. the closing CX is the very next op on it.
            nxt_ctrl = self._succ(order, pos, node, ctrl)
            if nxt_ctrl is None or self._key(nxt_ctrl) != self._key(close):
                continue
            raw = _raw_angle(rz)
            if raw is None:
                continue
            # Symbolic angles are kept: they cannot be tested against zero, but
            # they CAN be added together, and that is the one place this pass
            # beats Qiskit's own pipeline (see SOLUTION.md, milestone 3).
            found.append((node, rz, close, raw, _bound_angle(rz)))
        return found

    # -- rewrites -----------------------------------------------------------
    #
    # Each sweep applies *every* non-overlapping rewrite it can find before
    # rebuilding the wire index.  Rewriting one window and immediately
    # rescanning is much easier to write and is what the first draft did, but
    # it makes the pass O(rewrites x gates): on an 8-qubit, depth-100 circuit
    # with 50 plantable windows that is 50 full DAG traversals.  Batching
    # brings the measured cost back to ~linear in gate count (milestone 4).
    #
    # Removing nodes does not invalidate the rustworkx indices of the nodes
    # that remain, so the index built at the top of a sweep stays valid for
    # every window whose three nodes are still untouched -- hence the
    # ``consumed`` set.

    def _annihilate_all(self, dag: DAGCircuit, windows) -> int:
        period = TWO_PI if self.track_global_phase else FOUR_PI
        consumed: set[int] = set()
        n = 0
        for open_cx, rz, close_cx, _raw, theta in windows:
            if theta is None:                 # symbolic: cannot prove it is zero
                continue
            if not _is_multiple_of(theta, period, self.tol):
                continue
            keys = {self._key(open_cx), self._key(rz), self._key(close_cx)}
            if keys & consumed:
                continue
            if self.track_global_phase:
                dag.global_phase += theta / 2.0
            for node in (open_cx, rz, close_cx):
                dag.remove_op_node(node)
            consumed |= keys
            self.stats["annihilated"] += 1
            n += 1
        return n

    def _fuse_all(self, dag: DAGCircuit, windows) -> int:
        order, pos = self._wire_order(dag)
        by_open = {self._key(w[0]): w for w in windows}
        consumed: set[int] = set()
        n = 0
        for open_cx, rz, close_cx, raw, _theta in windows:
            ctrl, targ = open_cx.qargs
            keys = {self._key(open_cx), self._key(rz), self._key(close_cx)}
            if keys & consumed:
                continue
            # the next window must start exactly where this one ends, on *both*
            # wires -- otherwise something sits between the inner CX pair and
            # they do not cancel.
            nxt_t = self._succ(order, pos, close_cx, targ)
            nxt_c = self._succ(order, pos, close_cx, ctrl)
            if nxt_t is None or nxt_c is None:
                continue
            if self._key(nxt_t) != self._key(nxt_c):
                continue
            other = by_open.get(self._key(nxt_t))
            if other is None:
                continue
            open2, rz2, close2, raw2, _t2 = other
            if tuple(open2.qargs) != (ctrl, targ):
                continue
            keys2 = {self._key(open2), self._key(rz2), self._key(close2)}
            if keys2 & consumed:
                continue
            # CX . CX on the same pair is exactly the identity: drop the inner
            # pair and the second RZ, and sum the angles into the first RZ.
            # float + float, or ParameterExpression + anything -- both work.
            dag.substitute_node(rz, RZGate(raw + raw2), inplace=True)
            for node in (close_cx, open2, rz2):
                dag.remove_op_node(node)
            consumed |= keys | keys2
            self.stats["fused"] += 1
            n += 1
        return n

    def run(self, dag: DAGCircuit) -> DAGCircuit:
        self.stats = {"annihilated": 0, "fused": 0, "sweeps": 0}
        for _ in range(self.max_sweeps):
            self.stats["sweeps"] += 1
            windows = self._windows(dag)
            if not windows:
                break
            if self._fuse_all(dag, windows):
                continue
            if self._annihilate_all(dag, windows):
                continue
            break                   # fixed point reached -> the pass is idempotent
        return dag

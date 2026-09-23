#!/usr/bin/env python3
"""concept_map.py — the concept dependency graph with a mastery overlay.

Eighty-plus chapter files is past the point where a linear ladder is the right
way to navigate the corpus.  ``tools/concept_graph.json`` is a curated
prerequisite DAG over it: nodes are *concepts* (not files), each naming the
corpus files that teach it and the app categories that drill it.  This script
loads that graph, scores every concept against the shared study history, and
answers the only question that matters mid-study: **what am I ready to learn
next?**

Usage
-----
  tools/concept_map.py                  # terminal view + "ready to learn next"
  tools/concept_map.py --next 15        # longer ready list
  tools/concept_map.py --area qec       # one area only
  tools/concept_map.py --html           # exports/concept_map.html (self-contained)
  tools/concept_map.py --dot | dot -Tsvg -o map.svg
  tools/concept_map.py --check          # validate the graph against the repo

Mastery
-------
The weighting is **dashboard.py's**, imported, not reimplemented: every graded
encounter in every app's history is flattened by ``dashboard.iter_retention_events``
and decayed by ``dashboard._session_weight`` (14-day half-life).  A concept's
score is the decayed accuracy over the encounters in its drill categories, and
its *evidence* is the decayed count of those encounters — so one lucky answer
last month does not mark a concept mastered.  ``QUANTUM_STUDY_DATA_DIR`` is
honoured because dashboard.py honours it.

Stdlib only.  Never writes to the study data directory.
"""

from __future__ import annotations

import argparse
import ast
import html
import json
import math
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Optional

ROOT = Path(__file__).resolve().parent.parent
GRAPH_FILE = Path(__file__).resolve().parent / "concept_graph.json"
DEFAULT_HTML = ROOT / "exports" / "concept_map.html"
SCHEMA = "quantum-study/concept-graph@1"

# dashboard.py lives at the repo root and reads QUANTUM_STUDY_DATA_DIR at import
# time, exactly like the apps.  Importing it (rather than copying its extraction
# and decay) is deliberate: the history schemas are load-bearing and there must
# be exactly one parser for them in the repo.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import dashboard  # noqa: E402


# ---------------------------------------------------------------------------
# Mastery bands
#
# Ordinal states, so they are encoded three ways everywhere they appear
# (colour + glyph + written label) — colour alone never carries the meaning.
# Hexes are the data-viz status palette: good / warning / critical, plus a
# categorical blue for "looks good, not enough reps yet" and neutral grey for
# "no data".  red-vs-green is hard for deuteranopes, which is exactly why the
# glyph and the label ship with every node in the terminal view, the SVG, the
# tooltip and the legend.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Band:
    key: str
    label: str
    glyph: str
    ansi: str
    light: str
    dark: str


BANDS = {
    "mastered":  Band("mastered",  "mastered",   "●", "32", "#0ca30c", "#0ca30c"),
    "strong":    Band("strong",    "strong",     "■", "34", "#2a78d6", "#3987e5"),
    "learning":  Band("learning",  "learning",   "◆", "33", "#fab219", "#fab219"),
    "weak":      Band("weak",      "weak",       "▼", "31", "#d03b3b", "#d03b3b"),
    "untouched": Band("untouched", "untouched",  "·", "90", "#898781", "#898781"),
}
BAND_ORDER = ["mastered", "strong", "learning", "weak", "untouched"]


# ---------------------------------------------------------------------------
# Graph model
# ---------------------------------------------------------------------------

@dataclass
class Node:
    id: str
    label: str
    area: str
    docs: list[str]
    drills: list[dict]
    needs: list[str]
    # filled in later
    layer: int = 0
    dependents: list[str] = field(default_factory=list)
    score: Optional[float] = None      # decayed accuracy, 0-1
    evidence: float = 0.0              # decayed graded-item count
    encounters: int = 0                # raw encounter count
    band: str = "untouched"

    @property
    def mastered(self) -> bool:
        return self.band == "mastered"


@dataclass
class Graph:
    nodes: dict[str, Node]
    areas: list[dict]
    order: list[str]                   # topological order
    threshold: float
    min_evidence: float
    seen_evidence: float

    def __iter__(self) -> Iterator[Node]:
        return (self.nodes[i] for i in self.order)

    def area_label(self, area_id: str) -> str:
        for a in self.areas:
            if a["id"] == area_id:
                return a["label"]
        return area_id


class GraphError(Exception):
    """The graph file is malformed beyond the point where --check can help."""


def load_graph(path: Path = GRAPH_FILE) -> Graph:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise GraphError(f"graph file not found: {path}")
    except json.JSONDecodeError as exc:
        raise GraphError(f"{path}: invalid JSON — {exc}")
    if not isinstance(raw, dict):
        raise GraphError(f"{path}: top level must be an object")
    if raw.get("schema") != SCHEMA:
        raise GraphError(f"{path}: schema must be {SCHEMA!r}, got {raw.get('schema')!r}")

    nodes: dict[str, Node] = {}
    for entry in raw.get("nodes", []):
        if not isinstance(entry, dict) or not entry.get("id"):
            raise GraphError(f"{path}: every node needs an id")
        nid = entry["id"]
        if nid in nodes:
            raise GraphError(f"{path}: duplicate node id {nid!r}")
        nodes[nid] = Node(
            id=nid,
            label=str(entry.get("label") or nid),
            area=str(entry.get("area") or ""),
            docs=list(entry.get("docs", [])),
            drills=list(entry.get("drills", [])),
            needs=list(entry.get("needs", [])),
        )
    if not nodes:
        raise GraphError(f"{path}: no nodes")

    mastery = raw.get("mastery", {}) if isinstance(raw.get("mastery"), dict) else {}
    graph = Graph(
        nodes=nodes,
        areas=[a for a in raw.get("areas", []) if isinstance(a, dict) and a.get("id")],
        order=[],
        threshold=float(mastery.get("threshold", 0.80)),
        min_evidence=float(mastery.get("min_evidence", 5.0)),
        seen_evidence=float(mastery.get("seen_evidence", 0.5)),
    )
    for node in nodes.values():
        for prereq in node.needs:
            if prereq in nodes:
                nodes[prereq].dependents.append(node.id)
    graph.order = topological_order(graph)   # raises on a cycle
    assign_layers(graph)
    # Re-sort layer-major.  layer(prereq) < layer(node) always holds, so this is
    # still a topological order -- and it groups the listing the way you read it.
    area_rank = {a["id"]: n for n, a in enumerate(graph.areas)}
    graph.order.sort(key=lambda i: (graph.nodes[i].layer,
                                    area_rank.get(graph.nodes[i].area, 99),
                                    graph.nodes[i].label.lower(), i))
    return graph


def find_cycle(graph: Graph) -> Optional[list[str]]:
    """A prerequisite cycle as a node-id path, or None.  Iterative DFS."""
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {i: WHITE for i in graph.nodes}
    for start in graph.nodes:
        if colour[start] != WHITE:
            continue
        stack: list[tuple[str, Iterator[str]]] = [(start, iter(graph.nodes[start].needs))]
        path = [start]
        colour[start] = GREY
        while stack:
            nid, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                colour[nid] = BLACK
                stack.pop()
                path.pop()
                continue
            if nxt not in graph.nodes:
                continue                      # dangling: --check reports it
            if colour[nxt] == GREY:
                return path[path.index(nxt):] + [nxt]
            if colour[nxt] == WHITE:
                colour[nxt] = GREY
                path.append(nxt)
                stack.append((nxt, iter(graph.nodes[nxt].needs)))
    return None


def topological_order(graph: Graph) -> list[str]:
    """Kahn's algorithm, prerequisites first.  Raises GraphError on a cycle."""
    indeg = {i: 0 for i in graph.nodes}
    for node in graph.nodes.values():
        for prereq in node.needs:
            if prereq in graph.nodes:
                indeg[node.id] += 1
    area_rank = {a["id"]: n for n, a in enumerate(graph.areas)}

    def sort_key(nid: str) -> tuple:
        node = graph.nodes[nid]
        return (area_rank.get(node.area, 99), node.label.lower(), nid)

    ready = sorted([i for i, d in indeg.items() if d == 0], key=sort_key)
    out: list[str] = []
    while ready:
        nid = ready.pop(0)
        out.append(nid)
        newly: list[str] = []
        for dep in graph.nodes[nid].dependents:
            indeg[dep] -= 1
            if indeg[dep] == 0:
                newly.append(dep)
        if newly:
            ready = sorted(ready + newly, key=sort_key)
    if len(out) != len(graph.nodes):
        cycle = find_cycle(graph)
        detail = " -> ".join(cycle) if cycle else "unidentified"
        raise GraphError(f"prerequisite graph is cyclic: {detail}")
    return out


def assign_layers(graph: Graph) -> None:
    """layer(n) = longest prerequisite chain ending at n (roots are 0)."""
    for nid in graph.order:
        node = graph.nodes[nid]
        depths = [graph.nodes[p].layer + 1 for p in node.needs if p in graph.nodes]
        node.layer = max(depths, default=0)


# ---------------------------------------------------------------------------
# The app category vocabularies, read statically out of the apps
#
# Importing the apps is not an option (ten sibling packages that all define a
# top-level ``core``), so the category lists are read the way
# tools/export_cards.py reads the flashcard palette: parse the source, never
# duplicate the data.
# ---------------------------------------------------------------------------

def _module_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return [p for p in sorted(directory.rglob("*.py"))
            if p.stem != "__init__" and "__pycache__" not in p.parts]


def _kwarg_values(directory: Path, keyword: str) -> set[str]:
    """Collect ``keyword='literal'`` values from one-object-per-file modules."""
    pattern = re.compile(rf"^\s*{keyword}\s*=\s*(['\"])(.*?)\1\s*,?\s*$", re.M)
    found: set[str] = set()
    for path in _module_files(directory):
        for match in pattern.finditer(path.read_text(encoding="utf-8")):
            found.add(match.group(2))
    return found


def _module_assign(path: Path, name: str):
    """``name = <literal>`` at module level, evaluated safely."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for stmt in tree.body:
        targets: list[ast.expr] = []
        value: Optional[ast.expr] = None
        if isinstance(stmt, ast.Assign):
            targets, value = list(stmt.targets), stmt.value
        elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
            targets, value = [stmt.target], stmt.value
        for target in targets:
            if isinstance(target, ast.Name) and target.id == name and value is not None:
                return ast.literal_eval(value)
    raise KeyError(f"{path}: no module-level {name}")


def _enum_values(path: Path, class_name: str) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for stmt in ast.walk(tree):
        if isinstance(stmt, ast.ClassDef) and stmt.name == class_name:
            return {ast.literal_eval(s.value) for s in stmt.body
                    if isinstance(s, ast.Assign) and isinstance(s.value, ast.Constant)}
    raise KeyError(f"{path}: no class {class_name}")


def quiz_subjects(app_dir: str) -> dict[str, list[str]]:
    return _module_assign(ROOT / app_dir / "core" / "topics.py", "TOPICS")


def app_categories() -> dict[str, set[str]]:
    """{dashboard app name: the categories that app actually writes}."""
    cats: dict[str, set[str]] = {
        "Flashcard Drill": _kwarg_values(ROOT / "flashcard-drill" / "cards", "category"),
        "QEC Trainer":     _kwarg_values(ROOT / "qec-trainer" / "problems", "category"),
        "VQA Trainer":     _kwarg_values(ROOT / "vqa-trainer" / "problems", "category"),
        "Qiskit Dojo":    (set(_module_assign(ROOT / "qiskit-dojo" / "katas" / "__init__.py",
                                              "SECTION_ORDER"))
                           | _kwarg_values(ROOT / "qiskit-dojo" / "katas", "section")),
        "Exam Simulator": (set(_module_assign(ROOT / "exam-sim" / "config.py", "SECTIONS"))
                           | _kwarg_values(ROOT / "exam-sim" / "bank", "section")),
        "Math Quiz":       set(quiz_subjects("math-quiz")),
        "Quantum Quiz":    set(quiz_subjects("quantum-quiz")),
        "Circuit Trainer": _enum_values(ROOT / "circuit-trainer" / "core" / "models.py",
                                        "ProblemCategory"),
        # problems_history stores only {problem_id, kind}; the concept-level
        # vocabulary is the problem topics, plus the literal kind "derivation"
        # that derivation attempts are written with.
        "Problem Trainer": (_kwarg_values(ROOT / "problem-trainer" / "problems", "topic")
                            | {"derivation"}),
    }
    return cats


def _norm(text: str) -> str:
    return " ".join(str(text or "").split()).casefold()


def category_resolvers() -> dict[str, dict[str, str]]:
    """{app: {normalised history category -> canonical category}} for the two
    apps whose history does not store the canonical name directly."""
    resolvers: dict[str, dict[str, str]] = {}
    for app, app_dir in (("Math Quiz", "math-quiz"), ("Quantum Quiz", "quantum-quiz")):
        # iter_retention_events labels a quiz record with its *topic*; the graph
        # references the subject that owns it.
        table: dict[str, str] = {}
        for subject, topics in quiz_subjects(app_dir).items():
            table[_norm(subject)] = subject
            for topic in topics:
                table.setdefault(_norm(topic), subject)
        resolvers[app] = table
    # Problem Trainer labels an attempt with its kind; the id names the topic.
    table = {}
    pattern_id = re.compile(r"^\s*id\s*=\s*(['\"])(.*?)\1", re.M)
    pattern_topic = re.compile(r"^\s*topic\s*=\s*(['\"])(.*?)\1", re.M)
    for path in _module_files(ROOT / "problem-trainer" / "problems"):
        text = path.read_text(encoding="utf-8")
        mid, mtopic = pattern_id.search(text), pattern_topic.search(text)
        if mid and mtopic:
            table[_norm(mid.group(2))] = mtopic.group(2)
    resolvers["Problem Trainer"] = table
    return resolvers


# ---------------------------------------------------------------------------
# Mastery overlay
# ---------------------------------------------------------------------------

@dataclass
class HistorySummary:
    events: int
    apps_with_data: list[str]
    data_dir: Path
    matched: int
    unmatched: list[tuple[str, str, int]]   # (app, category, count) not in the graph


def load_history() -> dict[str, list]:
    return {name: dashboard._load(path) for name, path in dashboard._FILES.items()}


def score_graph(graph: Graph, raw: Optional[dict[str, list]] = None) -> HistorySummary:
    """Fold the study history into per-node decayed accuracy and evidence."""
    if raw is None:
        raw = load_history()
    events = dashboard.iter_retention_events(raw)
    resolvers = category_resolvers()

    # {(app, normalised category): [weighted_correct, weighted_total, count]}
    buckets: dict[tuple[str, str], list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
    for ev in events:
        table = resolvers.get(ev.app)
        category = ev.category
        if table is not None:
            category = (table.get(_norm(ev.item or "")) if ev.app == "Problem Trainer"
                        else table.get(_norm(ev.category))) or ev.category
        # dashboard's own 14-day half-life, not a copy of it.
        weight = dashboard._session_weight({"timestamp": ev.ts})
        bucket = buckets[(ev.app, _norm(category))]
        bucket[0] += weight * ev.correct
        bucket[1] += weight * ev.total
        bucket[2] += 1

    used: set[tuple[str, str]] = set()
    for node in graph.nodes.values():
        w_correct = w_total = 0.0
        count = 0
        for drill in node.drills:
            key = (drill.get("app", ""), _norm(drill.get("category", "")))
            if key not in buckets:
                continue
            used.add(key)
            c, t, n = buckets[key]
            w_correct += c
            w_total += t
            count += int(n)
        node.evidence = w_total
        node.encounters = count
        node.score = (w_correct / w_total) if w_total > 0 else None
        node.band = classify(node, graph)

    unmatched = sorted(
        ((app, cat, int(vals[2])) for (app, cat), vals in buckets.items()
         if (app, cat) not in used),
        key=lambda row: -row[2])
    return HistorySummary(
        events=len(events),
        apps_with_data=sorted(name for name, sessions in raw.items() if sessions),
        data_dir=dashboard.DATA_DIR,
        matched=len(used),
        unmatched=unmatched,
    )


def classify(node: Node, graph: Graph) -> str:
    if node.score is None or node.evidence < graph.seen_evidence:
        return "untouched"
    if node.score < 0.5:
        return "weak"
    if node.score < graph.threshold:
        return "learning"
    return "mastered" if node.evidence >= graph.min_evidence else "strong"


def ready_to_learn(graph: Graph) -> list[Node]:
    """Not mastered, but every prerequisite is.  Best unlock value first."""
    ready = [n for n in graph.nodes.values()
             if not n.mastered
             and all(graph.nodes[p].mastered for p in n.needs if p in graph.nodes)]
    position = {nid: i for i, nid in enumerate(graph.order)}
    ready.sort(key=lambda n: (-len(reachable_dependents(graph, n.id)),
                              position[n.id]))
    return ready


def reachable_dependents(graph: Graph, nid: str) -> set[str]:
    seen: set[str] = set()
    stack = list(graph.nodes[nid].dependents)
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(graph.nodes[cur].dependents)
    return seen


def drill_text(node: Node) -> str:
    if not node.drills:
        return "no drill coverage"
    return "; ".join(f"{d.get('app')} · {d.get('category')}" for d in node.drills)


# ---------------------------------------------------------------------------
# Terminal view
# ---------------------------------------------------------------------------

def _use_colour(mode: str) -> bool:
    if mode == "never":
        return False
    if mode == "always":
        return True
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


class Paint:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def __call__(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.enabled else text

    def band(self, text: str, band_key: str) -> str:
        return self(text, BANDS[band_key].ansi)

    def dim(self, text: str) -> str:
        return self(text, "2")

    def bold(self, text: str) -> str:
        return self(text, "1")


DASH = "─"
ELL = "…"


def _pct(node: Node) -> str:
    return "   —" if node.score is None else f"{node.score * 100:3.0f}%"


def render_terminal(graph: Graph, summary: HistorySummary, *,
                    next_n: int, area: Optional[str], paint: Paint) -> None:
    nodes = [n for n in graph if area is None or n.area == area]
    edges = sum(len(n.needs) for n in graph.nodes.values())

    print(paint.bold("Concept map"), f"— {len(graph.nodes)} concepts, {edges} prerequisite edges")
    print(f"  data dir : {summary.data_dir}")
    if summary.events:
        n_apps = len(summary.apps_with_data)
        print(f"  history  : {summary.events} graded encounters across "
              f"{n_apps} app{'' if n_apps == 1 else 's'} "
              f"({', '.join(summary.apps_with_data)})")
    else:
        print("  history  : no study history found — every concept is untouched")
    counts = {b: 0 for b in BAND_ORDER}
    for node in graph.nodes.values():
        counts[node.band] += 1
    legend = "  ".join(
        paint.band(f"{BANDS[b].glyph} {BANDS[b].label} {counts[b]}", b) for b in BAND_ORDER)
    print(f"  mastery  : {legend}")
    print(f"  rule     : mastered = decayed accuracy ≥ {graph.threshold:.0%} "
          f"over ≥ {graph.min_evidence:g} decayed reps")
    print()

    header = (f"  {'':1} {'concept':<52} {'area':<7} "
              f"{'acc':>4} {'reps':>6}  status")
    width = len(header)
    print(paint.dim(header))
    current_layer = None
    for node in nodes:
        if node.layer != current_layer:
            current_layer = node.layer
            in_layer = sum(1 for n in nodes if n.layer == current_layer)
            head = f"  {DASH * 2} layer {current_layer} ({in_layer}) "
            print(paint.dim(head + DASH * max(0, width - len(head))))
        label = node.label if len(node.label) <= 52 else node.label[:51] + ELL
        band = BANDS[node.band]
        line = (f"  {band.glyph} {label:<52} {node.area:<7} "
                f"{_pct(node):>4} {node.evidence:6.1f}  {band.label}")
        print(paint.band(line, node.band))
    print()

    ready = [n for n in ready_to_learn(graph) if area is None or n.area == area]
    print(paint.bold(f"READY TO LEARN NEXT") + f"  ({len(ready)} concept"
          f"{'' if len(ready) == 1 else 's'} unblocked; showing {min(next_n, len(ready))})")
    if not ready:
        print("  nothing is unblocked — finish a prerequisite first")
    for i, node in enumerate(ready[:next_n], 1):
        unlocks = len(reachable_dependents(graph, node.id))
        band = BANDS[node.band]
        print(f"  {i:>2}. " + paint.band(f"{band.glyph} {node.label}", node.band)
              + paint.dim(f"  [{graph.area_label(node.area)}]"))
        print(paint.dim(f"      unlocks {unlocks} concept{'' if unlocks == 1 else 's'}"
                        f" · {band.label} {_pct(node).strip()}"
                        f" · {node.evidence:.1f} reps"))
        for doc in node.docs:
            print(paint.dim(f"      read  {doc}"))
        print(paint.dim(f"      drill {drill_text(node)}"))
    print()

    uncovered = [n for n in graph.nodes.values() if not n.drills]
    if uncovered:
        print(paint.dim(f"note: {len(uncovered)} concept"
                        f"{' has' if len(uncovered) == 1 else 's have'} no drill "
                        f"coverage and can never leave 'untouched': "
                        + ", ".join(n.id for n in uncovered)))
    if summary.unmatched:
        shown = ", ".join(f"{app}/{cat} ({n})" for app, cat, n in summary.unmatched[:5])
        n = len(summary.unmatched)
        print(paint.dim(f"note: {n} history "
                        f"categor{'y matches' if n == 1 else 'ies match'} "
                        f"no concept: {shown}"))


# ---------------------------------------------------------------------------
# Graphviz output
# ---------------------------------------------------------------------------

def render_dot(graph: Graph) -> str:
    out: list[str] = [
        "digraph concept_map {",
        '  graph [rankdir=LR, splines=spline, fontname="Helvetica", bgcolor="#fcfcfb"];',
        '  node  [shape=box, style="rounded,filled", fontname="Helvetica", '
        'fontsize=10, penwidth=1.4];',
        '  edge  [color="#c3c2b7", arrowsize=0.6];',
    ]
    by_area: dict[str, list[Node]] = defaultdict(list)
    for node in graph:
        by_area[node.area].append(node)
    for area in graph.areas:
        members = by_area.get(area["id"], [])
        if not members:
            continue
        out.append(f'  subgraph "cluster_{area["id"]}" {{')
        out.append(f'    label="{_dot_escape(area["label"])}"; '
                   'fontsize=12; color="#e1e0d9";')
        for node in members:
            band = BANDS[node.band]
            tip = (f"{band.label} · "
                   f"{'no data' if node.score is None else f'{node.score:.0%}'} · "
                   f"{node.evidence:.1f} reps")
            out.append(
                f'    "{node.id}" [label="{_dot_escape(node.label)}", '
                f'color="{band.light}", fillcolor="{band.light}22", '
                f'tooltip="{_dot_escape(tip)}"];')
        out.append("  }")
    for node in graph:
        for prereq in node.needs:
            if prereq in graph.nodes:
                out.append(f'  "{prereq}" -> "{node.id}";')
    out.append("}")
    return "\n".join(out) + "\n"


def _dot_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


# ---------------------------------------------------------------------------
# HTML view — one self-contained file, inline SVG, no network of any kind
# ---------------------------------------------------------------------------

NODE_W, NODE_H = 236, 26
COL_PITCH, ROW_PITCH = 312, 34
PAD_X, PAD_Y = 28, 56


def layout(graph: Graph) -> dict[str, tuple[float, float]]:
    """Layered left-to-right placement, with two barycentre sweeps."""
    columns: dict[int, list[str]] = defaultdict(list)
    for nid in graph.order:                      # topological => stable start
        columns[graph.nodes[nid].layer].append(nid)
    index = {nid: i for col in columns.values() for i, nid in enumerate(col)}

    def sweep(layers: list[int], neighbours) -> None:
        for layer in layers:
            col = columns[layer]
            def bary(nid: str) -> float:
                near = [index[m] for m in neighbours(nid) if m in index]
                return sum(near) / len(near) if near else index[nid]
            col.sort(key=lambda nid: (bary(nid), graph.nodes[nid].label.lower()))
            for i, nid in enumerate(col):
                index[nid] = i

    ordered = sorted(columns)
    for _ in range(2):
        sweep(ordered[1:], lambda nid: graph.nodes[nid].needs)
        sweep(list(reversed(ordered[:-1])), lambda nid: graph.nodes[nid].dependents)

    # Centre every column on the tallest one: short columns hugging the top of a
    # 16-column canvas reads as a bug, and centring also shortens the edges.
    tallest = max(len(c) for c in columns.values())
    pos: dict[str, tuple[float, float]] = {}
    for layer, col in columns.items():
        top = PAD_Y + (tallest - len(col)) * ROW_PITCH / 2
        for i, nid in enumerate(col):
            pos[nid] = (PAD_X + layer * COL_PITCH, top + i * ROW_PITCH)
    return pos


def render_html(graph: Graph, summary: HistorySummary) -> str:
    pos = layout(graph)
    width = max(x for x, _ in pos.values()) + NODE_W + PAD_X
    height = max(y for _, y in pos.values()) + NODE_H + PAD_Y

    edges: list[str] = []
    for node in graph:
        x2, y2 = pos[node.id]
        for prereq in node.needs:
            if prereq not in pos:
                continue
            x1, y1 = pos[prereq]
            sx, sy = x1 + NODE_W, y1 + NODE_H / 2
            tx, ty = x2, y2 + NODE_H / 2
            cx = (tx - sx) * 0.45
            edges.append(
                f'<path class="edge" data-from="{node.id}" data-to="{prereq}" '
                f'd="M{sx:.1f},{sy:.1f} C{sx + cx:.1f},{sy:.1f} '
                f'{tx - cx:.1f},{ty:.1f} {tx:.1f},{ty:.1f}"/>')

    node_svg: list[str] = []
    for node in graph:
        x, y = pos[node.id]
        band = BANDS[node.band]
        label = node.label if len(node.label) <= 30 else node.label[:29] + "…"
        node_svg.append(
            f'<g class="node band-{node.band}" data-id="{node.id}" '
            f'transform="translate({x:.1f},{y:.1f})" tabindex="0" role="listitem">'
            f'<rect class="box" width="{NODE_W}" height="{NODE_H}" rx="5"/>'
            f'<rect class="cap" width="5" height="{NODE_H}" rx="2.5"/>'
            f'<text class="glyph" x="15" y="{NODE_H / 2 + 4:.0f}">{band.glyph}</text>'
            f'<text class="name" x="29" y="{NODE_H / 2 + 4:.0f}">{html.escape(label)}</text>'
            f'<title>{html.escape(node.label)} — {band.label}</title>'
            f'</g>')

    counts = {b: 0 for b in BAND_ORDER}
    for node in graph.nodes.values():
        counts[node.band] += 1
    ready = ready_to_learn(graph)

    payload = {
        "nodes": {
            n.id: {
                "label": n.label,
                "area": graph.area_label(n.area),
                "band": n.band,
                "bandLabel": BANDS[n.band].label,
                "glyph": BANDS[n.band].glyph,
                "score": None if n.score is None else round(n.score, 4),
                "evidence": round(n.evidence, 2),
                "encounters": n.encounters,
                "layer": n.layer,
                "docs": n.docs,
                "drills": [f"{d.get('app')} · {d.get('category')}" for d in n.drills],
                "needs": [p for p in n.needs if p in graph.nodes],
                "unlocks": sorted(reachable_dependents(graph, n.id)),
            } for n in graph.nodes.values()
        },
        "ready": [n.id for n in ready],
        "order": graph.order,
    }
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

    legend = "".join(
        f'<span class="key band-{b}"><span class="swatch"></span>'
        f'<span class="kglyph">{BANDS[b].glyph}</span>'
        f'{BANDS[b].label}<b>{counts[b]}</b></span>' for b in BAND_ORDER)
    rows = "".join(
        f'<tr class="band-{n.band}" data-id="{n.id}"><td>{n.layer}</td>'
        f'<td><span class="tglyph">{BANDS[n.band].glyph}</span>'
        f'{html.escape(n.label)}</td>'
        f'<td>{html.escape(graph.area_label(n.area))}</td>'
        f'<td class="num">{"—" if n.score is None else f"{n.score:.0%}"}</td>'
        f'<td class="num">{n.evidence:.1f}</td>'
        f'<td>{BANDS[n.band].label}</td></tr>' for n in graph)
    ready_html = "".join(
        f'<li data-id="{n.id}"><b>{html.escape(n.label)}</b>'
        f'<span class="meta">unlocks {len(reachable_dependents(graph, n.id))} '
        f'· {BANDS[n.band].label}</span></li>' for n in ready[:20]) or \
        "<li>nothing is unblocked</li>"

    n_apps = len(summary.apps_with_data)
    hist = (f"{summary.events} graded encounters across "
            f"{n_apps} app{'' if n_apps == 1 else 's'}"
            if summary.events else "no study history yet - every concept is untouched")

    css = _HTML_CSS
    js = _HTML_JS
    return f"""<!DOCTYPE html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Concept map — quantum study suite</title>
<style>
{css}
</style>
<body>
<header>
  <h1>Concept map</h1>
  <p class="sub">{len(graph.nodes)} concepts &middot;
     {sum(len(n.needs) for n in graph.nodes.values())} prerequisite edges &middot;
     {html.escape(hist)}</p>
  <p class="sub">mastered = decayed accuracy &ge; {graph.threshold:.0%} over
     &ge; {graph.min_evidence:g} decayed reps
     (dashboard.py's 14-day half-life)</p>
  <div class="legend">{legend}</div>
  <div class="controls">
    <input id="search" type="search" placeholder="filter concepts…" autocomplete="off">
    <button id="zoom-out" type="button">&minus;</button>
    <button id="zoom-in" type="button">+</button>
    <button id="zoom-fit" type="button">fit all</button>
    <button id="zoom-home" type="button">reset</button>
    <button id="toggle-table" type="button">table view</button>
    <span class="hint">drag to pan &middot; hover for detail &middot; click to pin a
      concept&rsquo;s prerequisites and unlocks</span>
  </div>
</header>

<main>
  <section id="graph-pane">
    <svg id="graph" viewBox="0 0 {width:.0f} {height:.0f}"
         role="list" aria-label="concept dependency graph">
      <g id="viewport">
        <g id="edges" aria-hidden="true">{''.join(edges)}</g>
        <g id="nodes">{''.join(node_svg)}</g>
      </g>
    </svg>
    <div id="tip" role="tooltip" hidden></div>
  </section>
  <aside>
    <h2>Ready to learn next</h2>
    <ol id="ready">{ready_html}</ol>
    <h2>Selected</h2>
    <div id="detail"><p class="muted">Click a concept in the graph.</p></div>
  </aside>
</main>

<section id="table" hidden>
  <table>
    <thead><tr><th>layer</th><th>concept</th><th>area</th><th>acc</th>
    <th>reps</th><th>status</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>

<script type="application/json" id="data">{data}</script>
<script>
{js}
</script>
</body>
</html>
"""


_HTML_CSS = """
:root {
  color-scheme: light;
  --surface: #fcfcfb; --plane: #f2f1ed; --panel: #ffffff;
  --ink: #0b0b0b; --ink2: #52514e; --muted: #898781;
  --grid: #e1e0d9; --edge: #c3c2b7; --edge-hi: #52514e;
  --mastered: #0ca30c; --strong: #2a78d6; --learning: #fab219;
  --weak: #d03b3b; --untouched: #898781;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --surface: #1a1a19; --plane: #0d0d0d; --panel: #222221;
    --ink: #ffffff; --ink2: #c3c2b7; --muted: #898781;
    --grid: #2c2c2a; --edge: #46453f; --edge-hi: #c3c2b7;
    --strong: #3987e5;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --surface: #1a1a19; --plane: #0d0d0d; --panel: #222221;
  --ink: #ffffff; --ink2: #c3c2b7; --muted: #898781;
  --grid: #2c2c2a; --edge: #46453f; --edge-hi: #c3c2b7;
  --strong: #3987e5;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--plane); color: var(--ink);
  font: 14px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif;
}
header { padding: 16px; border-bottom: 1px solid var(--grid); background: var(--surface); }
h1 { margin: 0 0 2px; font-size: 19px; letter-spacing: -0.01em; }
h2 { margin: 18px 0 6px; font-size: 13px; text-transform: uppercase;
     letter-spacing: 0.06em; color: var(--ink2); }
.sub { margin: 0; color: var(--ink2); font-size: 12.5px; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 14px; margin: 10px 0 8px; }
.key { display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px;
       color: var(--ink2); }
.key b { color: var(--ink); font-variant-numeric: tabular-nums; }
.swatch { width: 11px; height: 11px; border-radius: 3px; background: var(--c);
          border: 1px solid var(--c); }
.kglyph, .tglyph { color: var(--c); font-size: 12px; }
.tglyph { margin-right: 7px; }
.band-mastered  { --c: var(--mastered); }
.band-strong    { --c: var(--strong); }
.band-learning  { --c: var(--learning); }
.band-weak      { --c: var(--weak); }
.band-untouched { --c: var(--untouched); }
.controls { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
input[type=search] {
  padding: 5px 9px; border: 1px solid var(--grid); border-radius: 6px;
  background: var(--panel); color: var(--ink); font: inherit; min-width: 190px;
}
button {
  padding: 5px 11px; border: 1px solid var(--grid); border-radius: 6px;
  background: var(--panel); color: var(--ink); font: inherit; cursor: pointer;
}
button:hover { border-color: var(--edge-hi); }
.hint { color: var(--muted); font-size: 12px; }
main { display: grid; grid-template-columns: minmax(0,1fr) 310px; }
#graph-pane { position: relative; overflow: hidden; background: var(--surface);
              height: calc(100vh - 168px); min-height: 420px; }
#graph { width: 100%; height: 100%; cursor: grab; display: block; }
#graph.dragging { cursor: grabbing; }
.edge { fill: none; stroke: var(--edge); stroke-width: 1.1; }
.edge.up   { stroke: var(--strong); stroke-width: 2; }
.edge.down { stroke: var(--learning); stroke-width: 2; }
.node .box { fill: var(--c); fill-opacity: 0.14; stroke: var(--c); stroke-width: 1.2; }
.node .cap { fill: var(--c); }
.node .glyph { fill: var(--c); font-size: 12px; }
.node .name { fill: var(--ink); font-size: 12px; }
.node { cursor: pointer; }
.node:hover .box, .node:focus .box { fill-opacity: 0.3; stroke-width: 2; }
.node:focus { outline: none; }
svg.filtering .node { opacity: 0.16; }
svg.filtering .node.hit { opacity: 1; }
svg.pinned .node { opacity: 0.16; }
svg.pinned .node.rel { opacity: 1; }
svg.pinned .edge { opacity: 0.1; }
svg.pinned .edge.up, svg.pinned .edge.down { opacity: 1; }
#tip {
  position: absolute; pointer-events: none; max-width: 330px; z-index: 5;
  background: var(--panel); color: var(--ink); border: 1px solid var(--grid);
  border-radius: 8px; padding: 9px 11px; font-size: 12.5px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.18);
}
#tip h3 { margin: 0 0 4px; font-size: 13px; }
#tip dl { margin: 4px 0 0; display: grid; grid-template-columns: auto 1fr;
          gap: 2px 8px; }
#tip dt { color: var(--muted); }
#tip dd { margin: 0; }
aside { border-left: 1px solid var(--grid); background: var(--surface);
        padding: 12px 14px; overflow: auto; height: calc(100vh - 168px);
        min-height: 420px; }
#ready { margin: 0; padding-left: 20px; }
#ready li { margin-bottom: 7px; cursor: pointer; }
#ready li:hover b { text-decoration: underline; }
.meta { display: block; color: var(--muted); font-size: 12px; }
.muted { color: var(--muted); }
#detail ul { margin: 4px 0 8px; padding-left: 18px; }
#detail code { font-size: 11.5px; word-break: break-all; }
#table { padding: 14px 16px 40px; background: var(--plane); }
table { border-collapse: collapse; width: 100%; font-size: 12.5px; }
th, td { text-align: left; padding: 4px 8px; border-bottom: 1px solid var(--grid); }
th { color: var(--ink2); font-weight: 600; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
@media (max-width: 860px) {
  main { grid-template-columns: 1fr; }
  #graph-pane, aside { height: auto; }
  #graph-pane { height: 62vh; }
}
"""

_HTML_JS = r"""
(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("data").textContent);
  var svg = document.getElementById("graph");
  var viewport = document.getElementById("viewport");
  var tip = document.getElementById("tip");
  var pane = document.getElementById("graph-pane");
  var nodes = Array.prototype.slice.call(svg.querySelectorAll("g.node"));
  var edges = Array.prototype.slice.call(svg.querySelectorAll("path.edge"));
  var base = svg.getAttribute("viewBox").split(" ").map(Number);
  var view = base.slice();

  function setView() { svg.setAttribute("viewBox", view.join(" ")); }
  function zoom(factor, cx, cy) {
    var w = view[2] * factor, h = view[3] * factor;
    if (w < base[2] / 14 || w > base[2] * 4) return;
    view[0] = cx - (cx - view[0]) * factor;
    view[1] = cy - (cy - view[1]) * factor;
    view[2] = w; view[3] = h; setView();
  }
  function fit() { view = base.slice(); setView(); }
  // The graph is ~8x wider than it is tall; "fit everything" would shrink the
  // labels to nothing, so the opening view is the full height at 1:1 and as
  // much width as the pane can show.
  function home() {
    var r = svg.getBoundingClientRect();
    var aspect = (r.width && r.height) ? r.width / r.height : 2;
    view = [0, 0, Math.min(base[2], Math.max(base[3] * aspect, 700)), base[3]];
    setView();
  }

  document.getElementById("zoom-in").onclick = function () {
    zoom(0.8, view[0] + view[2] / 2, view[1] + view[3] / 2); };
  document.getElementById("zoom-out").onclick = function () {
    zoom(1.25, view[0] + view[2] / 2, view[1] + view[3] / 2); };
  document.getElementById("zoom-fit").onclick = fit;
  document.getElementById("zoom-home").onclick = home;

  function toUser(ev) {
    var r = svg.getBoundingClientRect();
    return [view[0] + (ev.clientX - r.left) / r.width * view[2],
            view[1] + (ev.clientY - r.top) / r.height * view[3]];
  }
  svg.addEventListener("wheel", function (ev) {
    ev.preventDefault();
    var p = toUser(ev);
    zoom(ev.deltaY > 0 ? 1.12 : 0.89, p[0], p[1]);
  }, { passive: false });

  var drag = null;
  svg.addEventListener("pointerdown", function (ev) {
    if (ev.button !== 0) return;
    drag = { x: ev.clientX, y: ev.clientY, vx: view[0], vy: view[1], moved: false };
    svg.classList.add("dragging");
    svg.setPointerCapture(ev.pointerId);
  });
  svg.addEventListener("pointermove", function (ev) {
    if (!drag) return;
    var r = svg.getBoundingClientRect();
    var dx = (ev.clientX - drag.x) / r.width * view[2];
    var dy = (ev.clientY - drag.y) / r.height * view[3];
    if (Math.abs(dx) + Math.abs(dy) > 2) drag.moved = true;
    view[0] = drag.vx - dx; view[1] = drag.vy - dy; setView();
  });
  function endDrag() { svg.classList.remove("dragging"); }
  svg.addEventListener("pointerup", function () { endDrag(); setTimeout(function () {
    drag = null; }, 0); });
  svg.addEventListener("pointercancel", function () { drag = null; endDrag(); });

  function pct(v) { return v === null ? "—" : Math.round(v * 100) + "%"; }

  function tipHTML(id) {
    var n = DATA.nodes[id];
    var docs = n.docs.map(function (d) {
      return "<li><code>" + d + "</code></li>"; }).join("");
    var drills = n.drills.length
      ? n.drills.map(function (d) { return "<li>" + d + "</li>"; }).join("")
      : "<li class='muted'>no drill coverage</li>";
    return "<h3>" + n.glyph + " " + n.label + "</h3>"
      + "<dl><dt>status</dt><dd>" + n.bandLabel + " · " + pct(n.score)
      + " over " + n.evidence.toFixed(1) + " decayed reps</dd>"
      + "<dt>area</dt><dd>" + n.area + "</dd>"
      + "<dt>needs</dt><dd>" + (n.needs.length || "none") + "</dd>"
      + "<dt>unlocks</dt><dd>" + n.unlocks.length + "</dd></dl>"
      + "<b>teaches</b><ul>" + docs + "</ul>"
      + "<b>drilled by</b><ul>" + drills + "</ul>";
  }

  function showTip(id, ev) {
    tip.innerHTML = tipHTML(id);
    tip.hidden = false;
    var r = pane.getBoundingClientRect();
    var x = ev.clientX - r.left + 14, y = ev.clientY - r.top + 14;
    if (x + tip.offsetWidth > r.width) x = r.width - tip.offsetWidth - 8;
    if (y + tip.offsetHeight > r.height) y = y - tip.offsetHeight - 26;
    tip.style.left = Math.max(4, x) + "px";
    tip.style.top = Math.max(4, y) + "px";
  }

  function ancestors(id) {
    var out = {}, stack = DATA.nodes[id].needs.slice();
    while (stack.length) {
      var cur = stack.pop();
      if (out[cur]) continue;
      out[cur] = 1;
      stack = stack.concat(DATA.nodes[cur].needs);
    }
    return out;
  }

  var pinned = null;
  function pin(id) {
    pinned = id;
    var up = ancestors(id), down = {};
    DATA.nodes[id].unlocks.forEach(function (d) { down[d] = 1; });
    nodes.forEach(function (g) {
      var nid = g.dataset.id;
      g.classList.toggle("rel", nid === id || !!up[nid] || !!down[nid]);
    });
    edges.forEach(function (e) {
      var a = e.dataset.to, b = e.dataset.from;
      e.classList.toggle("up", (b === id || !!up[b]) && (!!up[a] || a === id));
      e.classList.toggle("down", (b === id || !!down[b]) && (!!down[a] || a === id));
    });
    svg.classList.add("pinned");
    detail(id);
  }
  function unpin() {
    pinned = null;
    svg.classList.remove("pinned");
    nodes.forEach(function (g) { g.classList.remove("rel"); });
    edges.forEach(function (e) { e.classList.remove("up", "down"); });
  }

  function detail(id) {
    var n = DATA.nodes[id];
    document.getElementById("detail").innerHTML =
      tipHTML(id)
      + "<p class='muted'>prerequisites: "
      + (n.needs.map(function (p) { return DATA.nodes[p].label; }).join(", ") || "none")
      + "</p>";
  }

  nodes.forEach(function (g) {
    var id = g.dataset.id;
    g.addEventListener("pointerenter", function (ev) { showTip(id, ev); });
    g.addEventListener("pointermove", function (ev) { showTip(id, ev); });
    g.addEventListener("pointerleave", function () { tip.hidden = true; });
    g.addEventListener("focus", function () { detail(id); });
    g.addEventListener("click", function () {
      if (drag && drag.moved) return;
      if (pinned === id) { unpin(); } else { pin(id); }
    });
    g.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault();
        if (pinned === id) { unpin(); } else { pin(id); } }
    });
  });
  svg.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") unpin();
  });

  document.getElementById("search").addEventListener("input", function (ev) {
    var q = ev.target.value.trim().toLowerCase();
    if (!q) { svg.classList.remove("filtering"); return; }
    svg.classList.add("filtering");
    nodes.forEach(function (g) {
      var n = DATA.nodes[g.dataset.id];
      var hay = (n.label + " " + n.area + " " + n.docs.join(" ") + " "
                 + n.drills.join(" ")).toLowerCase();
      g.classList.toggle("hit", hay.indexOf(q) !== -1);
    });
  });

  Array.prototype.forEach.call(document.querySelectorAll("#ready li[data-id]"),
    function (li) { li.addEventListener("click", function () { pin(li.dataset.id); }); });

  var table = document.getElementById("table");
  var toggle = document.getElementById("toggle-table");
  toggle.addEventListener("click", function () {
    table.hidden = !table.hidden;
    toggle.textContent = table.hidden ? "table view" : "hide table";
  });
  home();
  window.addEventListener("resize", home);
})();
"""


# ---------------------------------------------------------------------------
# --check
# ---------------------------------------------------------------------------

CORPUS_REQUIRED = ("docs", "lesson-plans")
CORPUS_OPTIONAL = ("labs", "projects")


def _rel(path: Path) -> str:
    """Repo-relative when it can be, absolute otherwise (--graph may point out)."""
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def corpus_files(subdir: str) -> set[str]:
    base = ROOT / subdir
    return {str(p.relative_to(ROOT)) for p in sorted(base.rglob("*.md"))
            if p.name != "README.md"}


def check(graph_path: Path = GRAPH_FILE, *, strict: bool = False) -> int:
    failures: list[str] = []
    warnings: list[str] = []

    try:
        graph = load_graph(graph_path)
    except GraphError as exc:
        print(f"FAIL  {exc}")
        print("\n1 failure — the graph could not be loaded")
        return 1

    print(f"checking {_rel(graph_path)} "
          f"({len(graph.nodes)} nodes, "
          f"{sum(len(n.needs) for n in graph.nodes.values())} edges)")

    # -- structure ---------------------------------------------------------
    area_ids = {a["id"] for a in graph.areas}
    for node in graph.nodes.values():
        if not node.label:
            failures.append(f"{node.id}: empty label")
        if node.area not in area_ids:
            failures.append(f"{node.id}: unknown area {node.area!r}")
        if node.id in node.needs:
            failures.append(f"{node.id}: depends on itself")
        for prereq in node.needs:
            if prereq not in graph.nodes:
                failures.append(f"{node.id}: needs unknown concept {prereq!r}")
        if len(set(node.needs)) != len(node.needs):
            failures.append(f"{node.id}: duplicate entries in needs")
        if not node.docs:
            failures.append(f"{node.id}: teaches no corpus file")
    ok("structure: ids, labels, areas and edges resolve", failures)

    # -- acyclic -----------------------------------------------------------
    cycle = find_cycle(graph)
    if cycle:
        failures.append("prerequisite cycle: " + " -> ".join(cycle))
        print("FAIL  acyclic: " + " -> ".join(cycle))
    else:
        print(f"ok    acyclic: {len(graph.order)} concepts in "
              f"{max(n.layer for n in graph.nodes.values()) + 1} layers")

    # -- docs references ---------------------------------------------------
    missing: list[str] = []
    referenced: set[str] = set()
    for node in graph.nodes.values():
        for doc in node.docs:
            referenced.add(doc)
            path = ROOT / doc
            if not path.is_file():
                missing.append(f"{node.id}: docs file not found — {doc}")
    failures.extend(missing)
    if missing:
        for line in missing:
            print(f"FAIL  {line}")
    else:
        print(f"ok    corpus refs: {len(referenced)} files, all present")

    # -- corpus coverage ---------------------------------------------------
    # A chapter added since the graph was last curated is a gap in the graph,
    # not a broken reference, so it only fails under --strict: a new chapter
    # from someone else's branch must not break this check for everyone.
    for subdir in CORPUS_REQUIRED + CORPUS_OPTIONAL:
        uncovered = sorted(corpus_files(subdir) - referenced)
        required = subdir in CORPUS_REQUIRED
        if not uncovered:
            if required:
                print(f"ok    coverage: every {subdir}/ chapter is taught by a concept")
            continue
        for chapter in uncovered:
            line = f"chapter taught by no concept — {chapter}"
            if required and strict:
                failures.append(line)
                print(f"FAIL  {line}")
            else:
                warnings.append(line)

    # -- app categories ----------------------------------------------------
    try:
        vocab = app_categories()
    except (OSError, KeyError, SyntaxError, ValueError) as exc:
        failures.append(f"could not read the app category lists: {exc}")
        print(f"FAIL  could not read the app category lists: {exc}")
        vocab = {}
    if vocab:
        bad: list[str] = []
        used: set[tuple[str, str]] = set()
        for node in graph.nodes.values():
            for drill in node.drills:
                app, category = drill.get("app"), drill.get("category")
                if app not in dashboard._FILES:
                    bad.append(f"{node.id}: unknown app {app!r}")
                elif app not in vocab:
                    bad.append(f"{node.id}: app {app!r} exposes no categories")
                elif category not in vocab[app]:
                    near = sorted(c for c in vocab[app] if _norm(c) == _norm(category or ""))
                    hint = f" (did you mean {near[0]!r}?)" if near else ""
                    bad.append(f"{node.id}: {app} has no category "
                               f"{category!r}{hint}")
                else:
                    used.add((app, category))
        failures.extend(bad)
        for line in bad:
            print(f"FAIL  {line}")
        if not bad:
            print(f"ok    drills: {len(used)} distinct (app, category) pairs, all real")
        unused = sorted((app, c) for app, cs in vocab.items() for c in cs
                        if (app, c) not in used)
        if unused:
            warnings.append(f"{len(unused)} app categor"
                            f"{'y' if len(unused) == 1 else 'ies'} drilled by no concept: "
                            + ", ".join(f"{a}/{c}" for a, c in unused))
        for node in graph.nodes.values():
            if not node.drills:
                warnings.append(f"{node.id}: no drill coverage — mastery is unknowable")

    print()
    for line in warnings:
        print(f"warn  {line}")
    if failures:
        print(f"\n{len(failures)} failure{'' if len(failures) == 1 else 's'}")
        return 1
    print(f"\nall checks passed"
          f"{f' ({len(warnings)} warning' + ('' if len(warnings) == 1 else 's') + ')' if warnings else ''}")
    return 0


def ok(label: str, failures: list[str]) -> None:
    if not failures:
        print(f"ok    {label}")
    else:
        for line in failures:
            print(f"FAIL  {line}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        prog="concept_map.py",
        description="Concept dependency graph with a mastery overlay.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Mastery is computed with dashboard.py's decay; "
               "QUANTUM_STUDY_DATA_DIR is honoured.")
    ap.add_argument("--next", type=int, default=8, metavar="N",
                    help="how many 'ready to learn next' concepts to list (default 8)")
    ap.add_argument("--area", metavar="ID",
                    help="restrict the terminal listing to one area id")
    ap.add_argument("--html", action="store_true",
                    help=f"write a self-contained interactive graph to "
                         f"{DEFAULT_HTML.relative_to(ROOT)}")
    ap.add_argument("--dot", action="store_true",
                    help="emit Graphviz DOT instead of the terminal view")
    ap.add_argument("--check", action="store_true",
                    help="validate the graph against the repo and exit")
    ap.add_argument("--strict", action="store_true",
                    help="with --check: a corpus chapter that no concept teaches "
                         "is a failure, not a warning")
    ap.add_argument("--out", metavar="PATH", type=Path,
                    help="output path for --html / --dot")
    ap.add_argument("--graph", metavar="PATH", type=Path, default=GRAPH_FILE,
                    help="graph file to load (default tools/concept_graph.json)")
    ap.add_argument("--color", choices=("auto", "always", "never"), default="auto",
                    help="colourise the terminal view (default auto)")
    return ap.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    if args.check:
        return check(args.graph, strict=args.strict)

    try:
        graph = load_graph(args.graph)
    except GraphError as exc:
        print(f"concept_map: {exc}", file=sys.stderr)
        return 1
    if args.area and args.area not in {a["id"] for a in graph.areas}:
        print(f"concept_map: unknown area {args.area!r}; known: "
              + ", ".join(a["id"] for a in graph.areas), file=sys.stderr)
        return 2

    summary = score_graph(graph)

    if args.dot:
        text = render_dot(graph)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text, encoding="utf-8")
            print(f"wrote {args.out}", file=sys.stderr)
        else:
            sys.stdout.write(text)
        return 0

    if args.html:
        out = args.out or DEFAULT_HTML
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_html(graph, summary), encoding="utf-8")
        size = out.stat().st_size
        print(f"wrote {out} ({size / 1024:.0f} KB, {len(graph.nodes)} nodes, "
              f"self-contained)")
        return 0

    render_terminal(graph, summary, next_n=max(0, args.next), area=args.area,
                    paint=Paint(_use_colour(args.color)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

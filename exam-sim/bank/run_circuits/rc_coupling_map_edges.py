"""Question: rc_coupling_map_edges"""
from core.models import Question

QUESTION = Question(
    id='rc_coupling_map_edges',
    section='Run circuits',
    question='Which expression lists the directed qubit pairs a BackendV2 can apply two-qubit gates to?',
    options=[
        'backend.coupling_map.get_edges()',
        'backend.configuration().coupling_map',
        'backend.target.coupling_map',
        'backend.coupling_map()',
    ],
    correct_index=0,
    explanation='BackendV2.coupling_map is a property returning a CouplingMap, and CouplingMap.get_edges() yields the directed pairs. It is a property, not a method, so calling it raises TypeError; configuration() is the removed V1 accessor; and Target exposes connectivity through target.build_coupling_map(), not a coupling_map attribute.',
    difficulty='medium',
)

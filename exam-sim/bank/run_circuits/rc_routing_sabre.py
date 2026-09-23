"""Question: rc_routing_sabre"""
from core.models import Question

QUESTION = Question(
    id='rc_routing_sabre',
    section='Run circuits',
    question='Which statement about the routing stage of a preset pass manager is correct?',
    options=[
        'SabreSwap is the default routing pass at every preset optimization level, and its search is stochastic, so seed_transpiler is needed for reproducible output',
        'Routing is skipped at optimization_level=0 because no optimization is requested',
        'Routing runs only when the backend declares a symmetric coupling map',
        'Routing is deterministic, so two runs with identical inputs always give identical SWAP placement',
    ],
    correct_index=0,
    explanation='All preset levels route with SabreSwap (paired with Sabre layout at levels 1-3). Sabre uses randomized trials, so SWAP placement — and hence depth and CX count — can differ between runs unless you pass seed_transpiler. Routing is never skipped: even level 0 must satisfy connectivity, it just starts from a trivial layout.',
    difficulty='medium',
)

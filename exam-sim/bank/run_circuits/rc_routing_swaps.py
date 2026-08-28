"""Question: rc_routing_swaps"""
from core.models import Question

QUESTION = Question(
    id='rc_routing_swaps',
    section='Run circuits',
    question='A circuit applies cx(0, 2) but the target device only couples qubits (0,1) and (1,2) in a line. What does the transpiler do?',
    options=[
        'Inserts SWAP operations (decomposed to CX gates) to route the interaction, increasing the entangling-gate count',
        'Raises an error — the circuit cannot run on that device',
        'Applies the CX between qubits 0 and 1 instead, since 2 is unreachable',
        'Splits the CX into two smaller CX gates acting on adjacent pairs',
    ],
    correct_index=0,
    explanation='Routing moves logical qubits together by inserting SWAPs (each worth 3 CX) until every two-qubit gate acts on physically coupled qubits. The computation is preserved exactly — nothing is dropped or replaced — at the cost of extra entangling gates and depth.',
    difficulty='hard',
)

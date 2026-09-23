"""Question: rc_layout_method_trivial"""
from core.models import Question

QUESTION = Question(
    id='rc_layout_method_trivial',
    section='Run circuits',
    question='On a 5-qubit line backend, why does this produce 4 CX gates for a circuit containing only cx(0, 2)?\n\n```python\npm = generate_preset_pass_manager(optimization_level=1,\n                                  backend=backend,\n                                  layout_method="trivial")\nprint(pm.run(qc).count_ops()["cx"])   # 4\n```',
    options=[
        'layout_method="trivial" forces virtual qubit i onto physical qubit i, so 0 and 2 are not adjacent and routing inserts a SWAP (3 CX) on top of the original one',
        'layout_method="trivial" disables optimization entirely, so the CX is duplicated once per stage',
        'Trivial layout decomposes every CX into four CZ-equivalent CX gates',
        'The trivial layout reserves physical qubit 1 as an ancilla, forcing a longer route',
    ],
    correct_index=0,
    explanation='Overriding the layout stage with "trivial" replaces the layout *search* with the identity mapping. cx(0, 2) then spans physical 0 and 2, which are not coupled on a line, so SabreSwap inserts a SWAP (decomposed into 3 CX) — 4 CX in total. Leaving layout_method unset lets level 1 find an adjacent pair and keep a single CX.',
    difficulty='medium',
)

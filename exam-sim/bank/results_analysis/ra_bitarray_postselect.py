"""Question: ra_bitarray_postselect"""
from core.models import Question

QUESTION = Question(
    id='ra_bitarray_postselect',
    section='Results analysis',
    question="What does this print?\n\n```python\nfrom qiskit.primitives.containers import BitArray\n\nba = BitArray.from_counts({'00': 5, '01': 3, '10': 2, '11': 4})\nprint(ba.postselect([0], [1]).get_counts())\n```",
    options=[
        "{'01': 3, '11': 4} — only the shots whose clbit 0 equals 1 survive, keys unchanged",
        "{'1': 7} — postselect also drops the unselected bits, leaving only clbit 0 in the keys",
        "{'00': 5, '10': 2} — the selection value 1 means 'discard where the bit is 1'",
        "{'01': 3, '10': 2} — postselect compares the whole key against the selection list",
    ],
    correct_index=0,
    explanation='postselect(indices, selection) keeps only the shots whose listed clbits match the listed values and returns a BitArray of just those shots — here 3 + 4 = 7 of the original 14, with their full 2-bit keys intact. Use slice_bits() afterwards if you also want the conditioning bits removed. This is how heralded / mid-circuit-measurement experiments are filtered in the V2 world.',
    difficulty='hard',
)

"""Question: ra_bitarray_array_shape"""
from core.models import Question

QUESTION = Question(
    id='ra_bitarray_array_shape',
    section='Results analysis',
    question='A 3-qubit circuit with measure_all() was sampled for 100 shots. What does this print?\n\n```python\nba = result[0].data.meas\nprint(ba.array.shape, ba.to_bool_array().shape)\n```',
    options=[
        '(100, 1) (100, 3) — .array is bit-PACKED into uint8 bytes; to_bool_array() unpacks one bit per column',
        '(100, 3) (100, 3) — .array already stores one column per measured bit',
        '(3, 100) (100, 3) — .array is transposed relative to to_bool_array()',
        '(100,) (100, 3) — .array holds one integer outcome per shot',
    ],
    correct_index=0,
    explanation='BitArray keeps raw shot data packed eight bits to a byte, so `.array` has shape (num_shots, ceil(num_bits/8)) with dtype uint8 — (100, 1) for three measured bits, and it would widen to (100, 2) at nine bits. `to_bool_array()` unpacks it to one boolean column per bit, (100, 3). Indexing `.array` as if its columns were qubits is a silent, wrong-answer bug.',
    difficulty='hard',
)

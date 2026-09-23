"""Question: sa_packed_array"""
from core.models import Question

QUESTION = Question(
    id='sa_packed_array',
    section='Sampler',
    question='For a BitArray from a 1-bit classical register with 5 shots, what is bitarray.array.shape and dtype?',
    options=[
        '(5, 1) and uint8 — one row per shot, bits packed eight to a byte',
        '(5,) and bool — one boolean per shot',
        '(1, 5) and uint8 — one row per classical bit',
        '(5, 1) and float64 — probabilities per shot',
    ],
    correct_index=0,
    explanation='BitArray stores outcomes bit-packed: .array is a uint8 ndarray whose trailing axis is ceil(num_bits / 8) bytes and whose leading axes are (broadcast shape..., num_shots). For 1 bit and 5 shots that is (5, 1). Prefer get_counts()/get_bitstrings()/to_bool_array() over reading .array directly.',
    difficulty='hard',
)

"""Question: sa_join_data"""
from core.models import Question

QUESTION = Question(
    id='sa_join_data',
    section='Sampler',
    question='A circuit measures into two classical registers, "a" (1 bit) and "b" (1 bit), and the outcome is always a=1, b=0. What does result[0].join_data().get_counts() return?',
    options=[
        "{'01': <shots>} — join_data() concatenates the registers with the first-declared register in the least significant position",
        "{'10': <shots>} — registers are concatenated in declaration order, left to right",
        "{'1': <shots>, '0': <shots>} — join_data() returns one entry per register",
        'AttributeError — join_data() exists only on EstimatorPubResult',
    ],
    correct_index=0,
    explanation='SamplerPubResult.join_data() merges every BitArray field (or a named subset) into one BitArray, keeping Qiskit\'s little-endian convention: register "a" occupies the low bits and so prints on the right. With a=1 and b=0 the joined key is "01".',
    difficulty='hard',
)

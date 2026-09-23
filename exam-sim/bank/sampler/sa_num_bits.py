"""Question: sa_num_bits"""
from core.models import Question

QUESTION = Question(
    id='sa_num_bits',
    section='Sampler',
    question='For a BitArray produced from a 3-bit classical register run with 500 shots, what are num_bits and num_shots?',
    options=[
        'num_bits = 3 and num_shots = 500',
        'num_bits = 500 and num_shots = 3',
        'num_bits = 8 and num_shots = 500, because bits are packed into bytes',
        'num_bits = 3 and num_shots = 1500',
    ],
    correct_index=0,
    explanation='num_bits is the width of the register the BitArray came from and num_shots is how many samples were taken. (The underlying .array is packed into uint8 columns, but num_bits reports the logical width, not the padded storage.)',
    difficulty='easy',
)

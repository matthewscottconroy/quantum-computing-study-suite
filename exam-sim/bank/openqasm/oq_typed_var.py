"""Question: oq_typed_var"""
from core.models import Question

QUESTION = Question(
    id='oq_typed_var',
    section='OpenQASM',
    question='Which line declares a 32-bit signed integer classical variable in OpenQASM 3?',
    options=[
        'creg n[32];',
        'int n[32];',
        'bit[32] n;',
        'int[32] n;',
    ],
    correct_index=3,
    explanation='OpenQASM 3 has a real classical type system and writes the width in brackets after the type: int[32] n;, uint[8] m;, float[64] x;, bool flag;, and bit / bit[n] for measurement results. creg is the OpenQASM 2 spelling of a bit array, and bit[32] declares 32 bits, not an integer.',
    difficulty='easy',
)

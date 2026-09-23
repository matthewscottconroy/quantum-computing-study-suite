"""Question: ra_two_creg_databin"""
from core.models import Question

QUESTION = Question(
    id='ra_two_creg_databin',
    section='Results analysis',
    question='A V2 sampler runs a circuit with two classical registers, `alpha` and `beta`. How is the measured data laid out in the result?\n\n```python\ndata = result[0].data\n```',
    options=[
        'data.alpha and data.beta are two separate BitArrays, each with its own get_counts()',
        "data.meas holds one BitArray whose keys are space-separated, e.g. '0 1'",
        'data.c holds one BitArray with the registers concatenated into a single key',
        'Only the first register is returned; V2 supports one classical register per pub',
    ],
    correct_index=0,
    explanation="The V2 DataBin carries one field per classical register, named after that register — here data.alpha and data.beta, each a BitArray you call get_counts() on independently (list them with data.keys()). The space-separated '0 1' key is the V1 `Result.get_counts()` behaviour for multi-register circuits, and `data.meas` only exists because measure_all() creates a register literally called 'meas'.",
    difficulty='hard',
)

"""Question: oq_measure_all_export"""
from core.models import Question

QUESTION = Question(
    id='oq_measure_all_export',
    section='OpenQASM',
    question='A circuit built with qc.measure_all() is exported by qasm3.dumps(). What does the program declare?',
    options=[
        'bit[1] c; and a plain c[0] = measure q[0];',
        'creg meas[1]; with measure q[0] -> meas[0];',
        'bit[1] meas; with a barrier emitted before the measurement',
        'Nothing extra — measure_all() only flags the circuit for the sampler',
    ],
    correct_index=2,
    explanation='measure_all() appends a barrier and a brand-new classical register called "meas", so the export declares bit[1] meas; and writes meas[0] = measure q[0]; after barrier q[0];. The register is named "c" only if you created it yourself, and creg with -> is OpenQASM 2 spelling. The same "meas" name is what shows up as result[0].data.meas in a sampler result.',
    difficulty='medium',
)

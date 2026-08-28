"""Question: sa_creg_name"""
from core.models import Question

QUESTION = Question(
    id='sa_creg_name',
    section='Sampler',
    question='This code raises AttributeError: \'DataBin\' object has no attribute \'meas\'. Why?\n\n```python\nfrom qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister\nfrom qiskit.primitives import StatevectorSampler\n\nqr = QuantumRegister(1, "q")\ncr = ClassicalRegister(1, "c")\nqc = QuantumCircuit(qr, cr)\nqc.x(0)\nqc.measure(0, 0)\nresult = StatevectorSampler().run([qc]).result()\ncounts = result[0].data.meas.get_counts()\n```',
    options=[
        'The data field is named after the classical register — here it is result[0].data.c',
        'measure() must be replaced by measure_all() when using a Sampler',
        'The sampler strips classical registers with fewer than 2 bits',
        "DataBin only exposes 'meas' when shots are specified explicitly",
    ],
    correct_index=0,
    explanation="Sampler data fields mirror the circuit's classical register names. 'meas' only appears when measure_all() creates its default register; this circuit's register is named 'c', so the counts live at result[0].data.c. Any measurement style works with the sampler.",
    difficulty='hard',
)

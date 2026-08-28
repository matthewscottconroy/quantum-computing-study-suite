"""Question: sa_no_quasi_dists"""
from core.models import Question

QUESTION = Question(
    id='sa_no_quasi_dists',
    section='Sampler',
    question='A V1-era code sample reads `dist = job.result().quasi_dists[0]`. What is the V2 equivalent for a sampler pub whose circuit used measure_all()?',
    options=[
        'counts = job.result()[0].data.meas.get_counts() — V2 returns raw counts, not quasi-probabilities',
        'dist = job.result()[0].quasi_dists — the attribute simply moved onto the pub result',
        'dist = job.result().quasi_dists() — it became a method',
        'V2 samplers return probabilities directly via result[0].probabilities',
    ],
    correct_index=0,
    explanation='The V1 sampler post-processed shots into quasi-probability distributions; V2 deliberately returns the raw per-register shot data (BitArray), from which you take get_counts() and normalize yourself if you want probabilities. No quasi_dists attribute exists anywhere in V2 results.',
    difficulty='hard',
)

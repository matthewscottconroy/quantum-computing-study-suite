"""Question: ra_shot_noise_scaling"""
from core.models import Question

QUESTION = Question(
    id='ra_shot_noise_scaling',
    section='Results analysis',
    question='An estimate from 1000 shots has a statistical (shot-noise) uncertainty of about 0.016. Roughly how many shots are needed to halve that uncertainty?',
    options=[
        '4000 — the standard error falls as 1/√N, so cutting it in half costs 4× the shots',
        '2000 — the error is inversely proportional to the number of shots',
        '1414 — the error falls as 1/N², so √2 as many shots suffice',
        'It cannot be reduced by more shots; only error mitigation helps',
    ],
    correct_index=0,
    explanation='Sampling error on a frequency shrinks like 1/√N: σ = √(p(1−p)/N) is 0.0158 at N = 1000 and 0.0079 at N = 4000. Each extra decimal digit of precision therefore costs 100× the shots, which is why shot budgets dominate runtime planning. Only the STATISTICAL part shrinks this way — device bias stays put no matter how many shots you take, and that is what mitigation targets.',
    difficulty='medium',
)

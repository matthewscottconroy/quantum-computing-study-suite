"""Question: sa_pub_metadata_shots"""
from core.models import Question

QUESTION = Question(
    id='sa_pub_metadata_shots',
    section='Sampler',
    question='Where does a V2 sampler record how many shots a particular PUB actually ran?',
    options=[
        "result[0].metadata['shots']",
        "result.metadata['shots']",
        'result[0].data.shots',
        "result[0].header['shots']",
    ],
    correct_index=0,
    explanation='Each SamplerPubResult carries its own metadata dict, which includes the resolved shots for that PUB (plus circuit_metadata). The top-level PrimitiveResult.metadata holds run-wide information such as the version. Equivalently, result[0].data.<creg>.num_shots reports the same number from the BitArray.',
    difficulty='medium',
)

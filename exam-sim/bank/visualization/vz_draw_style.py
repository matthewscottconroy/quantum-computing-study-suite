"""Question: vz_draw_style"""
from core.models import Question

QUESTION = Question(
    id='vz_draw_style',
    section='Visualization',
    question='Which call renders a circuit in black and white for a print-ready figure?',
    options=[
        'qc.draw("mpl", style="bw")',
        'qc.draw("mpl", color=False)',
        'qc.draw("text", style="bw")',
        'qc.draw("bw")',
    ],
    correct_index=0,
    explanation='The mpl drawer takes style= as either a built-in name ("iqp", "bw", "clifford", "textbook") or a dict of overrides such as {"backgroundcolor": "#EEEEEE"}. The text drawer has no colours to restyle, there is no color= argument, and "bw" is a style, not an output mode.',
    difficulty='medium',
)

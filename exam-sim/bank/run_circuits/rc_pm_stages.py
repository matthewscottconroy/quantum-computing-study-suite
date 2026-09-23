"""Question: rc_pm_stages"""
from core.models import Question

QUESTION = Question(
    id='rc_pm_stages',
    section='Run circuits',
    question='A preset pass manager is a StagedPassManager. Which sequence names its stages, in order?',
    options=[
        'init, layout, routing, translation, optimization, scheduling',
        'layout, routing, optimization, translation',
        'unroll, map, optimize, schedule, assemble',
        'parse, validate, layout, routing, assemble, run',
    ],
    correct_index=0,
    explanation='generate_preset_pass_manager() returns a StagedPassManager whose .stages tuple is ("init", "layout", "routing", "translation", "optimization", "scheduling"). Knowing the order matters because you can replace any single stage (e.g. pm.layout = my_pass_manager) while keeping the rest of the preset.',
    difficulty='medium',
)

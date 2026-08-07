"""Card registry — one-file-per-card directory structure."""
from __future__ import annotations
import importlib
from pathlib import Path
from core.models import Flashcard


def all_cards() -> list[Flashcard]:
    cards: list[Flashcard] = []
    here = Path(__file__).parent
    for topic_dir in sorted(here.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith('_'):
            continue
        for card_file in sorted(topic_dir.glob('*.py')):
            if card_file.stem == '__init__':
                continue
            mod_name = f"cards.{topic_dir.name}.{card_file.stem}"
            try:
                mod = importlib.import_module(mod_name)
                if hasattr(mod, 'CARD'):
                    cards.append(mod.CARD)
            except Exception:
                pass
    return cards

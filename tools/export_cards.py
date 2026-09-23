#!/usr/bin/env python3
"""Export the flashcard-drill deck to portable formats.

The 550 cards live one-per-file under ``flashcard-drill/cards/``.  That is the
single source of truth; this script never copies card text into itself.  It
imports flashcard-drill's own loader (``cards.all_cards``) and re-emits the
deck as:

  cards.json         every card as ``{id, category, front, back}``
  quantum-study.apkg an Anki package, one subdeck per category, stable GUIDs
                     so a re-import *updates* the notes instead of duplicating
  index.html         a self-contained offline web deck (see tools/webdeck/)

Usage
-----
    python3 tools/export_cards.py --all                  # all three -> exports/
    python3 tools/export_cards.py --html --out _site     # just the web deck
    python3 tools/export_cards.py --json --apkg

With no format flag, ``--all`` is assumed.

Dependencies
------------
``--json`` and ``--html`` need nothing beyond the standard library: the card
modules and ``core.models`` are plain dataclasses, so the GitHub Pages build
runs on a bare Python with no pip install.  ``--apkg`` needs ``genanki``
(``pip install -r requirements-dev.txt``), imported lazily.

Determinism
-----------
Every output is byte-for-byte reproducible: no timestamps are written, the
deck/model ids and note GUIDs are derived from stable names, and the .apkg zip
is rebuilt with fixed entry metadata.  Re-running the exporter therefore
produces identical files, and re-importing the .apkg updates the existing
notes in place.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import html
import io
import json
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = REPO_ROOT / "flashcard-drill"
CARD_DIR = APP_DIR / "cards"
THEME_FILE = APP_DIR / "ui" / "theme.py"
WEBDECK_DIR = Path(__file__).resolve().parent / "webdeck"
DEFAULT_OUT = REPO_ROOT / "exports"

APKG_NAME = "quantum-study.apkg"
JSON_NAME = "cards.json"
HTML_NAME = "index.html"

ROOT_DECK = "Quantum Study"
# Anki ids are 64-bit ints; genanki's own docs use this range, so stay in it.
ID_FLOOR = 1 << 30
ID_SPAN = 1 << 30
# Fixed epoch for the .apkg so successive builds are byte-identical.
# 2024-01-01T00:00:00Z — arbitrary, but it must never change: it feeds the
# note/card row ids that Anki uses alongside the GUIDs.
APKG_TIMESTAMP = 1704067200.0
ZIP_DATE = (1980, 1, 1, 0, 0, 0)

# Fallback palette, only used if ui/theme.py stops carrying CATEGORY_COLORS.
FALLBACK_COLOR = "#58a6ff"


class ExportError(RuntimeError):
    """Anything that should stop the export with a readable message."""


# --------------------------------------------------------------- loading ---

@dataclass(frozen=True)
class Card:
    id: str
    category: str
    front: str
    back: str

    def as_dict(self) -> dict[str, str]:
        return {"id": self.id, "category": self.category,
                "front": self.front, "back": self.back}


def _expected_card_count() -> int:
    """How many card modules are on disk (``cards.all_cards`` swallows errors)."""
    return sum(1 for p in CARD_DIR.glob("*/*.py") if p.stem != "__init__")


def load_cards() -> list[Card]:
    """Load the deck through flashcard-drill's own registry.

    ``cards/__init__.py`` does ``from core.models import Flashcard``, so the app
    directory has to be the import root — hence the sys.path insert rather than
    a package-relative import.
    """
    if not CARD_DIR.is_dir():
        raise ExportError(f"card directory not found: {CARD_DIR}")

    app_dir = str(APP_DIR)
    inserted = app_dir not in sys.path
    if inserted:
        sys.path.insert(0, app_dir)
    try:
        from cards import all_cards  # type: ignore[import-not-found]
        raw = all_cards()
    except ImportError as exc:  # pragma: no cover - defensive
        raise ExportError(f"could not import flashcard-drill's card registry: {exc}") from exc
    finally:
        if inserted:
            try:
                sys.path.remove(app_dir)
            except ValueError:
                pass

    expected = _expected_card_count()
    if len(raw) != expected:
        # all_cards() catches per-module exceptions and skips the card, so a
        # broken card file would silently shrink the deck.  Refuse to ship one.
        raise ExportError(
            f"loaded {len(raw)} cards but {expected} card modules exist under "
            f"{CARD_DIR} — a card module failed to import; fix it before exporting"
        )
    if not raw:
        raise ExportError(f"no cards found under {CARD_DIR}")

    cards = [Card(id=c.id, category=c.category, front=c.front, back=c.back) for c in raw]

    seen: dict[str, str] = {}
    for c in cards:
        if c.id in seen:
            raise ExportError(f"duplicate card id {c.id!r} (categories "
                              f"{seen[c.id]!r} and {c.category!r})")
        seen[c.id] = c.category

    # Deterministic order: category, then id.  Keeps every output stable.
    cards.sort(key=lambda c: (c.category, c.id))
    return cards


def category_colors() -> dict[str, str]:
    """Read CATEGORY_COLORS out of ui/theme.py without importing PyQt6.

    theme.py imports QApplication at module scope, so it cannot be imported in
    a dependency-free build.  Parsing the literal keeps the web deck's colours
    in sync with the desktop app without duplicating the palette.
    """
    try:
        tree = ast.parse(THEME_FILE.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "CATEGORY_COLORS":
                try:
                    value = ast.literal_eval(node.value)
                except (ValueError, TypeError, SyntaxError):
                    return {}
                if isinstance(value, dict):
                    return {str(k): str(v) for k, v in value.items()}
    return {}


def category_counts(cards: list[Card]) -> list[tuple[str, int]]:
    """(category, card count) pairs, in a stable alphabetical order."""
    counts: dict[str, int] = {}
    for c in cards:
        counts[c.category] = counts.get(c.category, 0) + 1
    return [(name, counts[name]) for name in sorted(counts)]


def deck_meta(cards: list[Card]) -> dict[str, object]:
    """The header the web deck needs: totals, per-category counts, colours."""
    colors = category_colors()
    pairs = category_counts(cards)
    return {
        "total": len(cards),
        "categories": [{"name": name, "count": n} for name, n in pairs],
        "colors": {name: colors.get(name, FALLBACK_COLOR) for name, _ in pairs},
    }


# --------------------------------------------------------------- helpers ---

def stable_id(*parts: str) -> int:
    """A deterministic Anki deck/model id derived from a name."""
    digest = hashlib.sha256("::".join(parts).encode("utf-8")).digest()
    return ID_FLOOR + int.from_bytes(digest[:8], "big") % ID_SPAN


def anki_tag(category: str) -> str:
    """Anki tags cannot contain spaces; keep them readable and stable."""
    out = []
    for ch in category.replace("&", "and"):
        out.append(ch if (ch.isalnum() or ch in "-_") else "_")
    tag = "".join(out)
    while "__" in tag:
        tag = tag.replace("__", "_")
    return tag.strip("_")


def write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def human_size(n: int) -> str:
    return f"{n / 1024:.1f} KB" if n < 1024 * 1024 else f"{n / 1048576:.2f} MB"


# ---------------------------------------------------------------- exports ---

def export_json(cards: list[Card], out_dir: Path) -> Path:
    payload = {
        "schema": "quantum-study/cards@1",
        "source": "flashcard-drill/cards",
        "count": len(cards),
        "categories": [name for name, _ in category_counts(cards)],
        "cards": [c.as_dict() for c in cards],
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    return write_text(out_dir / JSON_NAME, text)


def export_apkg(cards: list[Card], out_dir: Path) -> Path:
    try:
        import genanki  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ExportError(
            "genanki is required for --apkg.  Install it with:\n"
            "    pip install -r requirements-dev.txt\n"
            "  (or: pip install 'genanki>=0.13')"
        ) from exc

    model = genanki.Model(
        stable_id("model", ROOT_DECK, "basic"),
        "Quantum Study Basic",
        fields=[{"name": "Front"}, {"name": "Back"}, {"name": "CardID"}],
        templates=[{
            "name": "Recall",
            "qfmt": '<div class="qs-front">{{Front}}</div>',
            "afmt": '{{FrontSide}}<hr id="answer">'
                    '<div class="qs-back">{{Back}}</div>'
                    '<div class="qs-id">{{CardID}}</div>',
        }],
        css=(
            ".card { font-family: -apple-system, 'Segoe UI', Roboto, sans-serif;"
            " font-size: 19px; text-align: left; padding: 14px; }\n"
            ".qs-front { font-weight: 600; }\n"
            ".qs-back { font-family: ui-monospace, 'DejaVu Sans Mono', monospace;"
            " font-size: 17px; line-height: 1.55; white-space: pre-wrap; }\n"
            ".qs-id { margin-top: 14px; font-size: 11px; opacity: .45;"
            " font-family: ui-monospace, monospace; }\n"
            ".card.nightMode .qs-id, .nightMode .qs-id { opacity: .55; }\n"
        ),
    )

    # An explicit parent deck keeps "Quantum Study" itself stable; Anki would
    # otherwise invent an id for it the first time a subdeck is imported.
    decks = {ROOT_DECK: genanki.Deck(
        stable_id("deck", ROOT_DECK), ROOT_DECK,
        description="Quantum computing flashcards exported from the "
                    "Quantum Computing Study Suite (tools/export_cards.py).")}

    for card in cards:
        name = f"{ROOT_DECK}::{card.category}"
        deck = decks.get(name)
        if deck is None:
            deck = genanki.Deck(stable_id("deck", name), name)
            decks[name] = deck
        note = genanki.Note(
            model=model,
            fields=[html.escape(card.front), html.escape(card.back), html.escape(card.id)],
            tags=["quantum-study", anki_tag(card.category)],
            guid=card.id,          # stable identity -> re-import updates in place
        )
        deck.add_note(note)

    package = genanki.Package([decks[k] for k in sorted(decks)])
    out_path = out_dir / APKG_NAME
    out_dir.mkdir(parents=True, exist_ok=True)

    tmp_dir = Path(tempfile.mkdtemp(prefix="qs-apkg-"))
    try:
        raw = tmp_dir / "raw.apkg"
        package.write_to_file(str(raw), timestamp=APKG_TIMESTAMP)
        _rewrite_zip_deterministically(raw, out_path)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return out_path


def _rewrite_zip_deterministically(src: Path, dst: Path) -> None:
    """Repack a zip with fixed entry timestamps so builds are byte-identical."""
    with zipfile.ZipFile(src) as zin:
        entries = [(info.filename, zin.read(info.filename)) for info in zin.infolist()]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in entries:
            info = zipfile.ZipInfo(name, date_time=ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zout.writestr(info, data)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(buf.getvalue())


def _read_template(name: str) -> str:
    path = WEBDECK_DIR / name
    if not path.is_file():
        raise ExportError(f"web deck template missing: {path}")
    return path.read_text(encoding="utf-8")


def _substitute(template: str, token: str, value: str) -> str:
    if template.count(token) < 1:
        raise ExportError(f"template placeholder {token} not found in tools/webdeck/index.html")
    return template.replace(token, value)


def export_html(cards: list[Card], out_dir: Path) -> Path:
    data = {"meta": deck_meta(cards), "cards": [c.as_dict() for c in cards]}
    # The JSON lives in a <script type="application/json"> block: escaping the
    # three markup-significant characters makes "</script>" in card text
    # impossible without changing what JSON.parse() returns.
    payload = (json.dumps(data, ensure_ascii=False, separators=(",", ":"))
               .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))

    page = _read_template("index.html")
    page = _substitute(page, "/*{{DECK_CSS}}*/", _read_template("deck.css").strip())
    page = _substitute(page, "/*{{DECK_JS}}*/", _read_template("deck.js").strip())
    page = _substitute(page, "{{DECK_DATA}}", payload)
    page = _substitute(page, "{{CARD_COUNT}}", str(len(cards)))
    page = _substitute(page, "{{CATEGORY_COUNT}}", str(len(category_counts(cards))))
    if "{{" in page:
        leftover = sorted({page[i:i + 40] for i in range(len(page)) if page.startswith("{{", i)})
        raise ExportError(f"unsubstituted placeholder(s) in the web deck: {leftover}")
    return write_text(out_dir / HTML_NAME, page)


# -------------------------------------------------------------------- cli ---

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="export_cards.py",
        description="Export the flashcard-drill deck to JSON, Anki and a static web deck.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="With no format flag, --all is assumed.",
    )
    parser.add_argument("--json", action="store_true", help=f"write {JSON_NAME}")
    parser.add_argument("--apkg", action="store_true", help=f"write {APKG_NAME} (needs genanki)")
    parser.add_argument("--html", action="store_true", help=f"write the self-contained {HTML_NAME}")
    parser.add_argument("--all", action="store_true", help="write all three (the default)")
    parser.add_argument("--out", metavar="DIR", type=Path, default=DEFAULT_OUT,
                        help=f"output directory (default: {DEFAULT_OUT.relative_to(REPO_ROOT)}/)")
    parser.add_argument("-q", "--quiet", action="store_true", help="only report errors")
    args = parser.parse_args(argv)

    want_json, want_apkg, want_html = args.json, args.apkg, args.html
    if args.all or not (want_json or want_apkg or want_html):
        want_json = want_apkg = want_html = True

    out_dir = args.out.expanduser().resolve()

    def say(msg: str) -> None:
        if not args.quiet:
            print(msg)

    try:
        cards = load_cards()
        say(f"loaded {len(cards)} cards in {len(category_counts(cards))} categories"
            f" from {CARD_DIR.relative_to(REPO_ROOT)}/")
        written: list[Path] = []
        if want_json:
            written.append(export_json(cards, out_dir))
        if want_apkg:
            written.append(export_apkg(cards, out_dir))
        if want_html:
            written.append(export_html(cards, out_dir))
    except ExportError as exc:
        print(f"export_cards.py: error: {exc}", file=sys.stderr)
        return 1

    for path in written:
        try:
            shown = path.relative_to(Path.cwd())
        except ValueError:
            shown = path
        say(f"  wrote {shown}  ({human_size(path.stat().st_size)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

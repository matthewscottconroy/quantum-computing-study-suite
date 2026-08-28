"""Thin wrapper around the Anthropic client — shared by grading and step-checking."""
from __future__ import annotations
import os
from config import API_KEY_FILE, MODEL


def get_api_key() -> str | None:
    if k := os.environ.get("ANTHROPIC_API_KEY"):
        return k
    if API_KEY_FILE.exists():
        return API_KEY_FILE.read_text().strip()
    return None


def has_api_key() -> bool:
    return get_api_key() is not None


def make_client():
    import anthropic
    key = get_api_key()
    if not key:
        raise RuntimeError(
            "No Anthropic API key found. Set ANTHROPIC_API_KEY or put a key in "
            f"{API_KEY_FILE}. You can still use “Show model solution” offline."
        )
    return anthropic.Anthropic(api_key=key), MODEL

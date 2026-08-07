"""Thin wrapper around the Anthropic client — shared by generation and grading."""
from __future__ import annotations
import os
from config import API_KEY_FILE, MODEL


def get_api_key() -> str | None:
    if k := os.environ.get("ANTHROPIC_API_KEY"):
        return k
    if API_KEY_FILE.exists():
        return API_KEY_FILE.read_text().strip()
    return None


def make_client():
    import anthropic
    key = get_api_key()
    if not key:
        raise RuntimeError("No Anthropic API key found.")
    return anthropic.Anthropic(api_key=key), MODEL

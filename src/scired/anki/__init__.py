"""Anki integration module."""

from scired.anki.client import AnkiClient
from scired.anki.deck import sync_words_to_anki

__all__ = ["AnkiClient", "sync_words_to_anki"]
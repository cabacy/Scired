"""Flashcard creation logic."""

import logging

from scired.anki.client import AnkiClient
from scired.config import settings
from scired.models.vocabulary import VocabEntry

logger = logging.getLogger(__name__)


def format_back(entry: VocabEntry) -> str:
    """Format the back of a flashcard."""
    parts = []

    if entry.translation:
        parts.append(f"<b>{entry.translation}</b>")

    if entry.context_sentence:
        parts.append(f"<i>{entry.context_sentence}</i>")

    if entry.timestamp is not None:
        parts.append(f"▶ {entry.timestamp_formatted}")

    if entry.source_video_title:
        parts.append(f"<small>Source: {entry.source_video_title}</small>")

    return "<br>".join(parts)


def sync_words_to_anki(
    entries: list[VocabEntry],
    client: AnkiClient | None = None,
) -> int:
    """
    Create Anki flashcards for vocabulary entries.

    Args:
        entries: List of vocabulary entries.
        client: AnkiClient instance (creates one if None).

    Returns:
        Number of cards created.
    """
    anki = client or AnkiClient()

    # Check if Anki is available
    if not anki.is_available():
        logger.warning("Anki is not available. Skipping sync.")
        return 0

    # Ensure deck exists
    anki.create_deck()

    created = 0
    skipped = 0

    for entry in entries:
        # Check for duplicates
        if anki.note_exists(entry.word):
            skipped += 1
            continue

        # Create the card
        back = format_back(entry)
        tags = [
            "scired",
            entry.cefr_level,
            entry.language,
            "youtube",
        ]

        note_id = anki.add_note(
            front=entry.word,
            back=back,
            tags=tags,
        )

        entry.anki_note_id = note_id
        created += 1

    logger.info(
        "Anki sync complete: %d created, %d skipped (duplicates)",
        created,
        skipped,
    )
    return created
"""AnkiConnect HTTP client."""

import logging

import requests

from scired.config import settings
from scired.exceptions import AnkiConnectionError

logger = logging.getLogger(__name__)


class AnkiClient:
    """Client for AnkiConnect API."""

    def __init__(self, url: str | None = None):
        self.url = url or settings.anki_url

    def _invoke(self, action: str, **params) -> dict:
        """Send a request to AnkiConnect."""
        try:
            response = requests.post(
                self.url,
                json={
                    "action": action,
                    "version": 6,
                    "params": params,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("error"):
                raise AnkiConnectionError(data["error"])

            return data.get("result")

        except requests.exceptions.ConnectionError:
            raise AnkiConnectionError(
                "Cannot connect to Anki. Make sure Anki is running "
                "and AnkiConnect plugin is installed."
            )
        except requests.exceptions.RequestException as e:
            raise AnkiConnectionError(f"Request failed: {e}")

    def is_available(self) -> bool:
        """Check if Anki is running and AnkiConnect is available."""
        try:
            self._invoke("version")
            return True
        except AnkiConnectionError:
            return False

    def create_deck(self, deck_name: str | None = None) -> None:
        """Create a deck if it doesn't exist."""
        deck = deck_name or settings.anki_deck_name
        self._invoke("createDeck", deck=deck)
        logger.info("Deck ensured: %s", deck)

    def add_note(
        self,
        front: str,
        back: str,
        tags: list[str] | None = None,
        deck_name: str | None = None,
    ) -> int:
        """Add a flashcard to Anki. Returns the note ID."""
        deck = deck_name or settings.anki_deck_name

        result = self._invoke(
            "addNote",
            note={
                "deckName": deck,
                "modelName": "Basic",
                "fields": {
                    "Front": front,
                    "Back": back,
                },
                "tags": tags or ["scired"],
            },
        )
        return result

    def find_notes(self, query: str) -> list[int]:
        """Find notes matching a query."""
        return self._invoke("findNotes", query=query) or []

    def note_exists(self, word: str, deck_name: str | None = None) -> bool:
        """Check if a note for this word already exists."""
        deck = deck_name or settings.anki_deck_name
        query = f'deck:"{deck}" word:{word}'
        notes = self.find_notes(query)
        return len(notes) > 0
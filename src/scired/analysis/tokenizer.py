"""Text tokenization — split text into words."""

import logging
import re

from scired.config import settings

logger = logging.getLogger(__name__)


def tokenize(text: str, language: str = "en") -> list[str]:
    """
    Tokenize text into lowercase words.

    Args:
        text: Input text.
        language: Language code (for future language-specific rules).

    Returns:
        List of lowercase words (letters only).
    """
    # Remove URLs, emails, numbers
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"\d+", "", text)

    # Extract words (letters, hyphens, apostrophes)
    if language == "de":
        # German: include umlauts, ß
        words = re.findall(r"[a-zA-ZäöüÄÖÜß]+(?:['-][a-zA-ZäöüÄÖÜß]+)*", text.lower())
    else:
        # English: standard
        words = re.findall(r"[a-zA-Z]+(?:['-][a-zA-Z]+)*", text.lower())

    # Filter by minimum length
    words = [w for w in words if len(w) >= settings.min_word_length]

    return words
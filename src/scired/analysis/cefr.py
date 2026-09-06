"""
CEFR level classification.

Maps word frequency (Zipf scale) to CEFR levels:
  Zipf ≥ 6.0  → A1 (very basic)
  Zipf ≥ 5.0  → A2
  Zipf ≥ 4.0  → B1
  Zipf ≥ 3.0  → B2
  Zipf ≥ 2.0  → C1
  Zipf < 2.0  → C2 (rare/academic)
"""

import logging
import statistics

from scired.analysis.frequency import get_zipf_frequency
from scired.analysis.tokenizer import tokenize
from scired.models.content import CEFRLevel

logger = logging.getLogger(__name__)

# Zipf → CEFR mapping
ZIPF_TO_CEFR: list[tuple[float, CEFRLevel]] = [
    (6.0, CEFRLevel.A1),
    (5.0, CEFRLevel.A2),
    (4.0, CEFRLevel.B1),
    (3.0, CEFRLevel.B2),
    (2.0, CEFRLevel.C1),
    (0.0, CEFRLevel.C2),
]


def classify_word(word: str, language: str = "en") -> CEFRLevel:
    """
    Classify a single word into a CEFR level.

    Args:
        word: The word to classify.
        language: Language code.

    Returns:
        CEFRLevel for the word.
    """
    zipf = get_zipf_frequency(word, language)

    for threshold, level in ZIPF_TO_CEFR:
        if zipf >= threshold:
            return level

    return CEFRLevel.C2


def classify_text(text: str, language: str = "en") -> CEFRLevel:
    """
    Classify an entire text into a CEFR level.

    Uses the median of all word levels.

    Args:
        text: The text to classify.
        language: Language code.

    Returns:
        Overall CEFR level for the text.
    """
    words = tokenize(text, language)

    if not words:
        return CEFRLevel.A1

    # Get numeric level for each word
    levels = [classify_word(w, language).numeric for w in words]

    # Use median (robust to outliers)
    median_level = statistics.median(levels)

    # Convert back to CEFRLevel
    median_int = round(median_level)
    for level in CEFRLevel:
        if level.numeric == median_int:
            return level

    return CEFRLevel.B2  # fallback


def get_level_distribution(text: str, language: str = "en") -> dict[str, int]:
    """
    Get distribution of CEFR levels in a text.

    Returns:
        Dict like {"A1": 120, "A2": 85, "B1": 45, ...}
    """
    words = tokenize(text, language)
    distribution: dict[str, int] = {level.value: 0 for level in CEFRLevel}

    for word in words:
        level = classify_word(word, language)
        distribution[level.value] += 1

    return distribution
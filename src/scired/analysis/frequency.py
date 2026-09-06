"""Word frequency lookup using wordfreq."""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Cache for frequency lookups
_freq_cache: dict[tuple[str, str], float] = {}


def get_zipf_frequency(word: str, language: str) -> float:
    """
    Get Zipf frequency for a word.

    Zipf scale:
      7.0+ → very common (the, is, have)
      4-7  → common
      2-4  → uncommon
      <2   → rare

    Args:
        word: The word to look up.
        language: Language code ("en", "de").

    Returns:
        Zipf frequency (0.0 if word not found).
    """
    cache_key = (word.lower(), language)

    if cache_key in _freq_cache:
        return _freq_cache[cache_key]

    try:
        from wordfreq import zipf_frequency
        freq = zipf_frequency(word.lower(), language)
    except Exception:
        freq = 0.0

    _freq_cache[cache_key] = freq
    return freq


def clear_cache() -> None:
    """Clear the frequency cache (useful for testing)."""
    _freq_cache.clear()
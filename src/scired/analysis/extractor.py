"""Extract difficult words from text."""

import logging

from scired.analysis.cefr import classify_word
from scired.analysis.tokenizer import tokenize
from scired.config import settings
from scired.models.content import CEFRLevel, TranscriptSegment
from scired.models.vocabulary import VocabEntry

logger = logging.getLogger(__name__)


def extract_difficult_words(
    segments: list[TranscriptSegment],
    language: str = "en",
    threshold: str | None = None,
) -> list[VocabEntry]:
    """
    Extract words above the CEFR threshold from transcript segments.

    Args:
        segments: Transcript segments with timestamps.
        language: Language code.
        threshold: CEFR threshold (e.g., "B2"). Defaults to settings.

    Returns:
        List of VocabEntry for words above threshold.
    """
    threshold_str = threshold or settings.default_threshold
    threshold_level = CEFRLevel(threshold_str)

    seen_words: set[str] = set()
    vocab_entries: list[VocabEntry] = []

    for segment in segments:
        words = tokenize(segment.text, language)

        for word in words:
            # Skip if already seen
            if word in seen_words:
                continue

            level = classify_word(word, language)

            if level >= threshold_level:
                seen_words.add(word)
                vocab_entries.append(
                    VocabEntry(
                        word=word,
                        language=language,
                        cefr_level=level.value,
                        context_sentence=segment.text,
                        timestamp=segment.start,
                    )
                )

    logger.info(
        "Extracted %d difficult words (threshold: %s+)",
        len(vocab_entries),
        threshold_str,
    )
    return vocab_entries
"""
YouTube subtitles extraction.

Strategy:
  1. Try manual subtitles (highest quality)
  2. Try auto-generated subtitles
  3. Raise SubtitlesNotFoundError if neither exists
"""

import logging

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
)

from scired.config import settings
from scired.exceptions import SubtitlesNotFoundError
from scired.models.content import TranscriptSegment

logger = logging.getLogger(__name__)


def get_youtube_transcript(
    video_id: str,
    language: str | None = None,
) -> list[TranscriptSegment]:
    """
    Fetch subtitles for a YouTube video.

    Args:
        video_id: YouTube video ID (e.g., "dQw4w9WgXcQ")
        language: Preferred language code. Defaults to settings.

    Returns:
        List of TranscriptSegment with text and timestamps.

    Raises:
        SubtitlesNotFoundError: If no subtitles are available.
    """
    lang = language or settings.preferred_subtitle_lang

    try:
        # Try to get transcript list
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Priority 1: Manual subtitles in preferred language
        try:
            transcript = transcript_list.find_manually_created_transcript([lang])
            logger.info("Found manual subtitles: %s", lang)
        except NoTranscriptFound:
            # Priority 2: Auto-generated in preferred language
            try:
                transcript = transcript_list.find_generated_transcript([lang])
                logger.info("Found auto-generated subtitles: %s", lang)
            except NoTranscriptFound:
                # Priority 3: Any available transcript
                try:
                    transcript = next(iter(transcript_list))
                    logger.warning(
                        "No %s subtitles, using '%s' instead",
                        lang, transcript.language_code,
                    )
                except StopIteration:
                    raise SubtitlesNotFoundError(video_id, "No transcripts available")

        # Fetch the actual transcript data
        raw_segments = transcript.fetch()

        # Convert to our model
        segments = [
            TranscriptSegment(
                text=seg["text"].strip(),
                start=seg["start"],
                duration=seg.get("duration", 0),
            )
            for seg in raw_segments
            if seg["text"].strip()
        ]

        logger.info(
            "Extracted %d segments (%d chars)",
            len(segments),
            sum(len(s.text) for s in segments),
        )
        return segments

    except TranscriptsDisabled:
        raise SubtitlesNotFoundError(video_id, "Transcripts are disabled for this video")
    except SubtitlesNotFoundError:
        raise
    except Exception as e:
        raise SubtitlesNotFoundError(video_id, f"Unexpected error: {e}")


def segments_to_text(segments: list[TranscriptSegment]) -> str:
    """Join segments into a single text string."""
    return " ".join(seg.text for seg in segments)
"""YouTube video source — orchestrates the full pipeline."""

import logging
import re

from scired.config import settings
from scired.exceptions import TranscriptionError
from scired.models.content import ContentItem, Language, SourceType
from scired.transcription.youtube_subs import get_youtube_transcript
from scired.transcription.whisper import transcribe_video

logger = logging.getLogger(__name__)


class YouTubeSource:
    """Handles fetching and processing YouTube videos."""

    def extract_video_id(self, url: str) -> str:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r"(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})",
            r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
            r"(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
            r"(?:youtube\.com/v/)([a-zA-Z0-9_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # Maybe it's already a video ID
        if re.match(r"^[a-zA-Z0-9_-]{11}$", url):
            return url

        raise TranscriptionError(url, "Could not extract video ID from URL")

    def get_video_metadata(self, video_id: str) -> dict:
        """Get video title, duration, channel using yt-dlp."""
        import yt_dlp

        url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get("title", "Unknown"),
                    "channel": info.get("channel", info.get("uploader", "Unknown")),
                    "duration": info.get("duration"),
                }
        except Exception as e:
            logger.warning("Could not fetch metadata: %s", e)
            return {"title": "Unknown", "channel": None, "duration": None}

    def fetch(self, url: str, language: str | None = None) -> ContentItem:
        """
        Full pipeline: URL → ContentItem with transcript.

        Strategy:
          1. Try YouTube subtitles
          2. Fall back to Whisper if no subtitles

        Args:
            url: YouTube URL.
            language: Language code. Auto-detect if None.

        Returns:
            ContentItem with transcript populated.
        """
        video_id = self.extract_video_id(url)
        lang = language or settings.preferred_subtitle_lang

        logger.info("Processing video: %s", video_id)

        # Get metadata
        metadata = self.get_video_metadata(video_id)

        # Try subtitles first
        segments = []
        transcript_source = "unknown"

        try:
            segments = get_youtube_transcript(video_id, lang)
            transcript_source = "youtube_subs"
            logger.info("Using YouTube subtitles")
        except TranscriptionError as e:
            logger.warning("Subtitles not available: %s", e)

            # Fallback to Whisper
            if settings.fallback_to_whisper:
                logger.info("Falling back to Whisper...")
                try:
                    segments = transcribe_video(url, lang)
                    transcript_source = "whisper"
                    logger.info("Whisper transcription successful")
                except TranscriptionError as we:
                    raise TranscriptionError(
                        video_id,
                        f"Both subtitles and Whisper failed: {we}",
                    )
            else:
                raise

        # Build ContentItem
        full_text = " ".join(seg.text for seg in segments)

        return ContentItem(
            video_id=video_id,
            title=metadata["title"],
            url=url,
            source_type=SourceType.YOUTUBE,
            language=Language(lang),
            channel=metadata["channel"],
            duration_seconds=metadata["duration"],
            segments=segments,
            transcript=full_text,
            transcript_source=transcript_source,
        )
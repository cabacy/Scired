"""
Whisper-based transcription (fallback when no subtitles).

Uses faster-whisper for local, offline transcription.
Requires: pip install faster-whisper
"""

import logging
import tempfile
from pathlib import Path

from scired.config import settings
from scired.exceptions import WhisperError
from scired.models.content import TranscriptSegment

logger = logging.getLogger(__name__)


def download_audio(video_url: str) -> Path:
    """
    Download audio from YouTube video using yt-dlp.

    Args:
        video_url: Full YouTube URL.

    Returns:
        Path to the downloaded audio file.
    """
    import yt_dlp

    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = str(Path(tmpdir) / "audio.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }
            ],
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            # Find the downloaded file
            audio_path = Path(tmpdir) / "audio.mp3"
            if not audio_path.exists():
                raise WhisperError("unknown", "Audio file not found after download")

            # Copy to a persistent temp location
            import shutil
            persistent_path = Path(tempfile.mktemp(suffix=".mp3"))
            shutil.copy2(audio_path, persistent_path)

            logger.info("Audio downloaded: %s", persistent_path)
            return persistent_path

        except Exception as e:
            raise WhisperError("unknown", f"Failed to download audio: {e}")


def transcribe_audio(
    audio_path: Path | str,
    language: str | None = None,
) -> list[TranscriptSegment]:
    """
    Transcribe audio file using faster-whisper.

    Args:
        audio_path: Path to audio file (mp3, wav, etc.)
        language: Language code ("en", "de"). Auto-detect if None.

    Returns:
        List of TranscriptSegment with text and timestamps.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise WhisperError(
            "unknown",
            "faster-whisper is not installed. Run: pip install faster-whisper",
        )

    model_name = settings.whisper_model
    logger.info("Loading Whisper model: %s", model_name)

    try:
        # Use CPU for MVP; switch to "cuda" if GPU available
        model = WhisperModel(model_name, device="cpu", compute_type="int8")

        logger.info("Transcribing: %s", audio_path)
        segments_gen, info = model.transcribe(
            str(audio_path),
            language=language,
            beam_size=5,
            vad_filter=True,  # Filter out silence
        )

        segments = []
        for seg in segments_gen:
            if seg.text.strip():
                segments.append(
                    TranscriptSegment(
                        text=seg.text.strip(),
                        start=seg.start,
                        duration=seg.end - seg.start,
                    )
                )

        logger.info(
            "Whisper transcription complete: %d segments, language=%s (%.0f%%)",
            len(segments),
            info.language,
            info.language_probability * 100,
        )
        return segments

    except Exception as e:
        raise WhisperError("unknown", f"Whisper failed: {e}")
    finally:
        # Clean up audio file
        if isinstance(audio_path, Path) and audio_path.exists():
            audio_path.unlink(missing_ok=True)


def transcribe_video(video_url: str, language: str | None = None) -> list[TranscriptSegment]:
    """
    Full pipeline: download audio → transcribe with Whisper.

    Args:
        video_url: YouTube URL.
        language: Language code.

    Returns:
        List of TranscriptSegment.
    """
    audio_path = download_audio(video_url)
    return transcribe_audio(audio_path, language)
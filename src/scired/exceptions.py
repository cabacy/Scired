"""
Exception hierarchy for Scired.

SciredError
├── TranscriptionError    — subtitle/whisper failures
├── NetworkError          — HTTP / connection issues
├── AnalysisError         — CEFR classification problems
├── StorageError          — database issues
└── AnkiConnectionError   — AnkiConnect unavailable
"""


class SciredError(Exception):
    """Base exception for all Scired errors."""


class TranscriptionError(SciredError):
    """Failed to get transcript from video."""

    def __init__(self, video_id: str, reason: str):
        self.video_id = video_id
        self.reason = reason
        super().__init__(f"[Transcription] Video '{video_id}': {reason}")


class SubtitlesNotFoundError(TranscriptionError):
    """No subtitles available for the video."""


class WhisperError(TranscriptionError):
    """Whisper transcription failed."""


class NetworkError(SciredError):
    """HTTP or connection error."""

    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"[Network] {url}: {reason}")


class AnalysisError(SciredError):
    """Error during CEFR analysis."""


class StorageError(SciredError):
    """Database operation failed."""


class AnkiConnectionError(SciredError):
    """Anki is not running or AnkiConnect is not available."""

    def __init__(self, reason: str = "Anki is not running or AnkiConnect plugin is missing"):
        super().__init__(f"[Anki] {reason}")
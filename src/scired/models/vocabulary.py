"""Vocabulary entry model — a word to learn."""

from pydantic import BaseModel


class VocabEntry(BaseModel):
    """A vocabulary item extracted from content."""

    word: str
    language: str  # "en" | "de"
    cefr_level: str  # "B2" | "C1" | "C2"
    translation: str | None = None
    context_sentence: str | None = None
    timestamp: float | None = None  # seconds into the video
    source_video_id: str | None = None
    source_video_title: str | None = None
    anki_note_id: int | None = None

    @property
    def timestamp_formatted(self) -> str:
        """Format timestamp as MM:SS."""
        if self.timestamp is None:
            return ""
        minutes = int(self.timestamp // 60)
        seconds = int(self.timestamp % 60)
        return f"{minutes:02d}:{seconds:02d}"
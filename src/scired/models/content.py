"""Content item model — represents a video/transcript."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, HttpUrl, field_validator


class SourceType(str, Enum):
    """Where the content came from."""
    YOUTUBE = "youtube"


class Language(str, Enum):
    """Supported languages."""
    EN = "en"
    DE = "de"


class CEFRLevel(str, Enum):
    """CEFR proficiency levels."""
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

    @property
    def numeric(self) -> int:
        """Numeric value for comparison."""
        return {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}[self.value]

    def __ge__(self, other: "CEFRLevel") -> bool:
        return self.numeric >= other.numeric

    def __gt__(self, other: "CEFRLevel") -> bool:
        return self.numeric > other.numeric

    def __le__(self, other: "CEFRLevel") -> bool:
        return self.numeric <= other.numeric

    def __lt__(self, other: "CEFRLevel") -> bool:
        return self.numeric < other.numeric


class TranscriptSegment(BaseModel):
    """A single segment of a transcript with timestamp."""
    text: str
    start: float = 0.0       # seconds
    duration: float = 0.0    # seconds


class ContentItem(BaseModel):
    """A piece of content: video, podcast, article."""

    # Identity
    video_id: str
    title: str
    url: str
    source_type: SourceType = SourceType.YOUTUBE
    language: Language = Language.EN

    # Metadata
    channel: str | None = None
    duration_seconds: int | None = None
    published_date: datetime | None = None

    # Content
    segments: list[TranscriptSegment] = []
    transcript: str = ""
    transcript_source: str = "unknown"  # "youtube_subs" | "whisper"

    # Analysis (filled later)
    cefr_level: CEFRLevel | None = None
    word_count: int = 0
    difficult_words: list[str] = []

    @field_validator("transcript")
    @classmethod
    def transcript_not_empty(cls, v: str) -> str:
        if len(v.strip()) < 50:
            raise ValueError("Transcript is too short (< 50 chars)")
        return v.strip()

    @property
    def full_text(self) -> str:
        """Get the full transcript as a single string."""
        if self.transcript:
            return self.transcript
        return " ".join(seg.text for seg in self.segments)
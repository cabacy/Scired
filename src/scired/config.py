"""
Global settings for Scired.

Values are loaded from:
  1. Environment variables (highest priority)
  2. .env file in project root
  3. Defaults defined below
"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """All application settings in one place."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="SCIRED_",
        extra="ignore",
    )

    # ─── Logging ────────────────────────────────────────────────────────
    log_level: str = "INFO"
    log_file: Path = PROJECT_ROOT / "data" / "scired.log"

    # ─── Transcription ──────────────────────────────────────────────────
    preferred_subtitle_lang: str = "en"
    fallback_to_whisper: bool = True
    whisper_model: str = Field(default="base", description="tiny|base|small|medium|large")

    # ─── Analysis ───────────────────────────────────────────────────────
    default_threshold: str = Field(default="B2", description="CEFR threshold for difficult words")
    min_word_length: int = Field(default=3, ge=2)

    # ─── Anki ───────────────────────────────────────────────────────────
    anki_url: str = "http://127.0.0.1:8765"
    anki_deck_name: str = "Scired::Vocabulary"

    # ─── Storage ────────────────────────────────────────────────────────
    db_path: Path = PROJECT_ROOT / "data" / "scired.db"
    transcripts_dir: Path = PROJECT_ROOT / "data" / "transcripts"

    def ensure_dirs(self) -> None:
        """Create necessary directories if they don't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
"""SQLite repository for content and vocabulary."""

import json
import logging
import sqlite3
from pathlib import Path

from scired.config import settings
from scired.exceptions import StorageError
from scired.models.content import ContentItem
from scired.models.vocabulary import VocabEntry

logger = logging.getLogger(__name__)


class Repository:
    """SQLite-based storage for Scired data."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or settings.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        with self._get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    source_type TEXT NOT NULL DEFAULT 'youtube',
                    language TEXT NOT NULL DEFAULT 'en',
                    channel TEXT,
                    duration_seconds INTEGER,
                    transcript TEXT,
                    transcript_source TEXT DEFAULT 'unknown',
                    cefr_level TEXT,
                    word_count INTEGER DEFAULT 0,
                    difficult_words TEXT DEFAULT '[]',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS vocabulary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    language TEXT NOT NULL,
                    cefr_level TEXT NOT NULL,
                    translation TEXT,
                    context_sentence TEXT,
                    timestamp REAL,
                    source_video_id TEXT,
                    anki_note_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(word, language, source_video_id)
                );
            """)
        logger.debug("Database initialized: %s", self.db_path)

    def save_content(self, item: ContentItem) -> int:
        """Save or update a content item. Returns the row ID."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO content
                    (video_id, title, url, source_type, language,
                     channel, duration_seconds, transcript, transcript_source,
                     cefr_level, word_count, difficult_words)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(video_id) DO UPDATE SET
                    title=excluded.title,
                    transcript=excluded.transcript,
                    cefr_level=excluded.cefr_level,
                    word_count=excluded.word_count,
                    difficult_words=excluded.difficult_words
                """,
                (
                    item.video_id,
                    item.title,
                    item.url,
                    item.source_type.value,
                    item.language.value,
                    item.channel,
                    item.duration_seconds,
                    item.full_text,
                    item.transcript_source,
                    item.cefr_level.value if item.cefr_level else None,
                    item.word_count,
                    json.dumps(item.difficult_words),
                ),
            )
            conn.commit()
            return cursor.lastrowid or 0

    def save_vocabulary(self, entries: list[VocabEntry]) -> int:
        """Save vocabulary entries. Returns count of new entries."""
        new_count = 0
        with self._get_conn() as conn:
            for entry in entries:
                try:
                    conn.execute(
                        """
                        INSERT INTO vocabulary
                            (word, language, cefr_level, translation,
                             context_sentence, timestamp, source_video_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            entry.word,
                            entry.language,
                            entry.cefr_level,
                            entry.translation,
                            entry.context_sentence,
                            entry.timestamp,
                            entry.source_video_id,
                        ),
                    )
                    new_count += 1
                except sqlite3.IntegrityError:
                    pass  # Duplicate, skip
            conn.commit()
        return new_count

    def get_content_by_video_id(self, video_id: str) -> ContentItem | None:
        """Retrieve content by video ID."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM content WHERE video_id = ?", (video_id,)
            ).fetchone()

            if not row:
                return None

            return ContentItem(
                video_id=row["video_id"],
                title=row["title"],
                url=row["url"],
                language=row["language"],
                channel=row["channel"],
                duration_seconds=row["duration_seconds"],
                transcript=row["transcript"] or "",
                transcript_source=row["transcript_source"],
                word_count=row["word_count"] or 0,
                difficult_words=json.loads(row["difficult_words"] or "[]"),
            )

    def is_video_processed(self, video_id: str) -> bool:
        """Check if video has already been processed."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM content WHERE video_id = ?", (video_id,)
            ).fetchone()
            return row is not None

    def get_statistics(self) -> dict:
        """Get overall statistics."""
        with self._get_conn() as conn:
            total_videos = conn.execute("SELECT COUNT(*) FROM content").fetchone()[0]
            total_words = conn.execute("SELECT COUNT(*) FROM vocabulary").fetchone()[0]
            levels = dict(
                conn.execute(
                    "SELECT cefr_level, COUNT(*) FROM vocabulary GROUP BY cefr_level"
                ).fetchall()
            )
            return {
                "total_videos": total_videos,
                "total_words": total_words,
                "words_by_level": levels,
            }
"""Transcription module — convert video/audio to text."""

from scired.transcription.youtube_subs import get_youtube_transcript
from scired.transcription.whisper import transcribe_audio

__all__ = ["get_youtube_transcript", "transcribe_audio"]
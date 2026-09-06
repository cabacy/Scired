"""Tests for YouTube subtitle extraction (mocked)."""

import pytest
from unittest.mock import patch, MagicMock

from scired.exceptions import SubtitlesNotFoundError
from scired.transcription.youtube_subs import get_youtube_transcript


class TestGetYoutubeTranscript:
    @patch("scired.transcription.youtube_subs.YouTubeTranscriptApi")
    def test_success(self, mock_api):
        """Should return segments when subtitles exist."""
        mock_transcript = MagicMock()
        mock_transcript.fetch.return_value = [
            {"text": "Hello world", "start": 0.0, "duration": 2.0},
            {"text": "Second line", "start": 2.0, "duration": 2.0},
        ]

        mock_list = MagicMock()
        mock_list.find_manually_created_transcript.return_value = mock_transcript
        mock_api.list_transcripts.return_value = mock_list

        segments = get_youtube_transcript("test_id", "en")

        assert len(segments) == 2
        assert segments[0].text == "Hello world"
        assert segments[0].start == 0.0

    @patch("scired.transcription.youtube_subs.YouTubeTranscriptApi")
    def test_no_subtitles(self, mock_api):
        """Should raise SubtitlesNotFoundError when no subtitles."""
        from youtube_transcript_api._errors import NoTranscriptFound

        mock_list = MagicMock()
        mock_list.find_manually_created_transcript.side_effect = NoTranscriptFound
        mock_list.find_generated_transcript.side_effect = NoTranscriptFound
        mock_list.__iter__ = MagicMock(return_value=iter([]))
        mock_api.list_transcripts.return_value = mock_list

        with pytest.raises(SubtitlesNotFoundError):
            get_youtube_transcript("test_id", "en")
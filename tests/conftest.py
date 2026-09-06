"""Shared test fixtures."""

import pytest

from scired.models.content import TranscriptSegment


@pytest.fixture
def sample_segments():
    """Sample transcript segments."""
    return [
        TranscriptSegment(text="Hello everyone, welcome to this video.", start=0.0, duration=3.0),
        TranscriptSegment(text="Today we will discuss ubiquitous technologies.", start=3.0, duration=4.0),
        TranscriptSegment(text="The infrastructure is paramount for development.", start=7.0, duration=4.0),
        TranscriptSegment(text="Thank you for watching.", start=11.0, duration=2.0),
    ]


@pytest.fixture
def sample_text():
    """Sample text for analysis."""
    return (
        "Hello everyone, welcome to this video. "
        "Today we will discuss ubiquitous technologies. "
        "The infrastructure is paramount for development. "
        "Thank you for watching."
    )
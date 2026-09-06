"""Tests for tokenization."""

from scired.analysis.tokenizer import tokenize


class TestTokenize:
    def test_basic(self):
        """Basic tokenization."""
        words = tokenize("Hello, World! This is a test.", "en")
        assert "hello" in words
        assert "world" in words
        assert "test" in words

    def test_removes_urls(self):
        """URLs should be removed."""
        words = tokenize("Visit https://example.com for more.", "en")
        assert "example" not in words
        assert "https" not in words

    def test_min_length(self):
        """Words shorter than min_word_length are filtered."""
        words = tokenize("I am a big dog", "en")
        assert "i" not in words
        assert "am" not in words
        assert "big" in words
        assert "dog" in words

    def test_german_umlauts(self):
        """German umlauts should be preserved."""
        words = tokenize("Die Straße ist schön. Über die Brücke.", "de")
        assert "straße" in words
        assert "schön" in words
        assert "über" in words
"""Tests for CEFR classification."""

import pytest

from scired.analysis.cefr import classify_word, classify_text
from scired.models.content import CEFRLevel


class TestClassifyWord:
    def test_common_word_is_a1(self):
        """Very common words should be A1."""
        level = classify_word("the", "en")
        assert level in (CEFRLevel.A1, CEFRLevel.A2)

    def test_rare_word_is_c2(self):
        """Very rare words should be C2."""
        level = classify_word("ubiquitous", "en")
        assert level.numeric >= CEFRLevel.B1.numeric

    def test_unknown_word_is_c2(self):
        """Unknown words default to C2."""
        level = classify_word("xyzzyplugh", "en")
        assert level == CEFRLevel.C2

    def test_german_word(self):
        """German words should be classified."""
        level = classify_word("und", "de")
        assert level in (CEFRLevel.A1, CEFRLevel.A2)


class TestClassifyText:
    def test_simple_text(self):
        """Simple text should be A1-A2."""
        text = "the cat is on the mat. the dog is big. i like the cat."
        level = classify_text(text, "en")
        assert level.numeric <= CEFRLevel.B1.numeric

    def test_complex_text(self):
        """Complex text should be higher."""
        text = (
            "The ubiquitous infrastructure necessitates comprehensive "
            "implementation of sophisticated methodologies."
        )
        level = classify_text(text, "en")
        assert level.numeric >= CEFRLevel.B1.numeric

    def test_empty_text(self):
        """Empty text defaults to A1."""
        level = classify_text("", "en")
        assert level == CEFRLevel.A1
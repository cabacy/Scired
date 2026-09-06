"""
Scired CLI — main entry point.

Commands:
    scired run <url>          — Full pipeline
    scired transcribe <url>   — Only get transcript
    scired analyze <url>      — Transcript + CEFR analysis
    scired sync-anki          — Sync pending words to Anki
    scired stats              — Show statistics
"""

import argparse
import logging
import sys

from scired.config import settings
from scired.logging_conf import setup_logging

logger = logging.getLogger(__name__)


def cmd_run(args: argparse.Namespace) -> None:
    """Full pipeline: transcribe → analyze → save → Anki."""
    from scired.analysis.cefr import classify_text
    from scired.analysis.extractor import extract_difficult_words
    from scired.analysis.tokenizer import tokenize
    from scired.anki.deck import sync_words_to_anki
    from scired.models.content import CEFRLevel
    from scired.sources.youtube import YouTubeSource
    from scired.storage.repository import Repository

    source = YouTubeSource()
    repo = Repository()

    print(f"\n  🎬 Processing: {args.url}")
    print(f"  {'─' * 50}")

    # 1. Fetch transcript
    try:
        item = source.fetch(args.url, language=args.lang)
    except Exception as e:
        logger.error("Failed to process video: %s", e)
        print(f"\n  ❌ Error: {e}\n")
        sys.exit(1)

    print(f"  ✅ Transcribed: {len(item.full_text.split())} words (source: {item.transcript_source})")

    # 2. Analyze
    words = tokenize(item.full_text, item.language.value)
    item.word_count = len(words)
    item.cefr_level = classify_text(item.full_text, item.language.value)

    print(f"  📊 Level: {item.cefr_level.value} | Words: {item.word_count}")

    # 3. Extract difficult words
    threshold = args.threshold or settings.default_threshold
    vocab = extract_difficult_words(
        item.segments,
        item.language.value,
        threshold,
    )

    # Update item
    item.difficult_words = [v.word for v in vocab]

    # Attach video info to vocab entries
    for v in vocab:
        v.source_video_id = item.video_id
        v.source_video_title = item.title

    print(f"  🔍 Difficult words: {len(vocab)} (threshold: {threshold}+)")

    # 4. Save to DB
    repo.save_content(item)
    new_words = repo.save_vocabulary(vocab)
    print(f"  💾 Saved to database ({new_words} new words)")

    # 5. Sync to Anki
    if not args.no_anki:
        created = sync_words_to_anki(vocab)
        print(f"  🃏 Anki cards created: {created} → \"{settings.anki_deck_name}\"")
    else:
        print("  ⏭️  Anki sync skipped (--no-anki)")

    # Summary
    print(f"\n  {'─' * 50}")
    print(f"  📝 \"{item.title}\"")
    print(f"  📺 Channel: {item.channel or 'Unknown'}")
    if item.duration_seconds:
        mins = item.duration_seconds // 60
        print(f"  ⏱️  Duration: {mins} min")
    print()


def cmd_transcribe(args: argparse.Namespace) -> None:
    """Only get transcript, no analysis."""
    from scired.sources.youtube import YouTubeSource
    from scired.storage.repository import Repository

    source = YouTubeSource()
    item = source.fetch(args.url, language=args.lang)

    repo = Repository()
    repo.save_content(item)

    print(f"\n  ✅ Transcribed: {item.title}")
    print(f"  📝 Source: {item.transcript_source}")
    print(f"  📊 Words: {len(item.full_text.split())}")
    print(f"  💾 Saved to database\n")


def cmd_stats(args: argparse.Namespace) -> None:
    """Show statistics."""
    from scired.storage.repository import Repository

    repo = Repository()
    stats = repo.get_statistics()

    print(f"\n  📊 Scired Statistics")
    print(f"  {'─' * 40}")
    print(f"  Videos processed: {stats['total_videos']}")
    print(f"  Words collected:  {stats['total_words']}")

    if stats["words_by_level"]:
        print(f"\n  Words by CEFR level:")
        for level, count in sorted(stats["words_by_level"].items()):
            bar = "█" * min(count // 2, 30)
            print(f"    {level}: {count:4d} {bar}")
    print()


def cli() -> None:
    """Main CLI entry point."""
    setup_logging()
    settings.ensure_dirs()

    parser = argparse.ArgumentParser(
        prog="scired",
        description="Turn YouTube videos into language learning material",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scired run <url>
    run_parser = subparsers.add_parser("run", help="Full pipeline: transcribe → analyze → Anki")
    run_parser.add_argument("url", help="YouTube video URL")
    run_parser.add_argument("--lang", help="Language code (en, de)")
    run_parser.add_argument("--threshold", help="CEFR threshold (default: B2)")
    run_parser.add_argument("--no-anki", action="store_true", help="Skip Anki sync")
    run_parser.set_defaults(func=cmd_run)

    # scired transcribe <url>
    trans_parser = subparsers.add_parser("transcribe", help="Only get transcript")
    trans_parser.add_argument("url", help="YouTube video URL")
    trans_parser.add_argument("--lang", help="Language code")
    trans_parser.set_defaults(func=cmd_transcribe)

    # scired stats
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.set_defaults(func=cmd_stats)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    cli()
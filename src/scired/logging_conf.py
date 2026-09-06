"""Logging configuration for the entire application."""

import logging
import sys

from scired.config import settings


def setup_logging() -> None:
    """
    Configure logging for the whole app. Call once at startup.

    Format:
        14:32:07 │ INFO     │ scired.transcription │ Downloaded subtitles
    """
    log_format = "%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s"
    date_format = "%H:%M:%S"

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if settings.log_file.parent.exists():
        handlers.append(
            logging.FileHandler(settings.log_file, encoding="utf-8")
        )

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
        force=True,
    )

    # Suppress noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def render_pdf(midi_path: str, output_path: str) -> str | None:
    """Convert MIDI to PDF via MuseScore. Returns output_path or None if MuseScore unavailable."""
    try:
        result = subprocess.run(
            ["mscore3", "-o", output_path, midi_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            logger.warning(f"MuseScore failed: {result.stderr}")
            return None
        logger.info(f"PDF saved: {output_path}")
        return output_path
    except FileNotFoundError:
        # MuseScore not installed — soft fail, pipeline continues
        logger.warning("MuseScore not found, skipping PDF render")
        return None
    except subprocess.TimeoutExpired:
        logger.warning("MuseScore timed out")
        return None
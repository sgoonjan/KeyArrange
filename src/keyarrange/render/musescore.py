import logging
import subprocess
from pathlib import Path

import music21
from music21 import stream, clef, note, tempo, meter

from keyarrange.dataclasses import Note as KANote

logger = logging.getLogger(__name__)


def render_pdf(
    right_hand: list[KANote],
    left_hand: list[KANote],
    output_path: str,
    bpm: float = 120.0,
) -> str | None:
    try:
        right_part = _notes_to_part(right_hand, clef.TrebleClef(), "Right Hand", bpm)
        left_part  = _notes_to_part(left_hand,  clef.BassClef(),  "Left Hand", bpm)

        score = stream.Score()
        score.insert(0, meter.TimeSignature("4/4"))
        score.insert(0, tempo.MetronomeMark(number=bpm))
        score.append(right_part)
        score.append(left_part)

        xml_path = str(Path(output_path).with_suffix(".musicxml"))
        score.write("musicxml", fp=xml_path)

        result = subprocess.run(
            ["mscore3", "-o", output_path, xml_path],
            capture_output=True, text=True, timeout=60
        )

        if result.returncode != 0:
            logger.warning(f"MuseScore failed: {result.stderr}")
            return None

        logger.info(f"PDF saved: {output_path}")
        return output_path

    except FileNotFoundError:
        logger.warning("MuseScore not found, skipping PDF render")
        return None
    except subprocess.TimeoutExpired:
        logger.warning("MuseScore timed out")
        return None
    except Exception as e:
        logger.warning(f"PDF render failed: {e}")
        return None


def _notes_to_part(notes: list[KANote], part_clef, part_name: str, bpm: float) -> stream.Part:
    part = stream.Part()
    part.partName = part_name
    part.insert(0, part_clef)

    for n in sorted(notes, key=lambda x: x.start):
        m21_note = note.Note(n.pitch)
        offset_quarters   = _quantize_offset(_seconds_to_quarters(n.start, bpm))
        m21_note.duration = _quantize_duration(_seconds_to_quarters(n.duration, bpm))
        m21_note.volume.velocity = n.velocity
        part.insert(offset_quarters, m21_note)

    return part


def _seconds_to_quarters(seconds: float, bpm: float) -> float:
    return seconds * (bpm / 60.0)


def _quantize_duration(duration_quarters: float) -> music21.duration.Duration:
    # Snap to nearest standard duration — MusicXML can't express irrational values
    standard = [4.0, 3.0, 2.0, 1.5, 1.0, 0.75, 0.5, 0.375, 0.25, 0.125]
    nearest = min(standard, key=lambda d: abs(d - duration_quarters))
    return music21.duration.Duration(nearest)


def _quantize_offset(offset_quarters: float) -> float:
    # Snap to nearest sixteenth note grid (0.25 quarter notes)
    return round(offset_quarters / 0.25) * 0.25
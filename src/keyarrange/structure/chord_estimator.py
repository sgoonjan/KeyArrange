import logging
from keyarrange.dataclasses import Note

logger = logging.getLogger(__name__)

# Chord quality intervals relative to root
_CHORD_TEMPLATES = {
    "major":      [0, 4, 7],
    "minor":      [0, 3, 7],
    "diminished": [0, 3, 6],
    "augmented":  [0, 4, 8],
}

_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def estimate_chords(
    notes: list[Note],
    beat_times: list[float],
    scale: str,
) -> list[tuple[str, float]]:
    """Returns list of (chord_label, beat_time) e.g. [('C major', 0.0), ('G major', 1.2)]."""
    chords = []

    for i, beat_start in enumerate(beat_times):
        beat_end = beat_times[i + 1] if i + 1 < len(beat_times) else beat_start + 0.5

        # Collect pitch classes active in this beat window
        active = set()
        for note in notes:
            if note.start < beat_end and note.end > beat_start:
                active.add(note.pitch % 12)

        if not active:
            # No notes — carry forward previous chord or use scale tonic
            label = chords[-1][0] if chords else _tonic_chord(scale)
        else:
            label = _best_chord(active)

        chords.append((label, beat_start))

    return chords


def _best_chord(pitch_classes: set[int]) -> str:
    """Match pitch classes against chord templates, return best label."""
    best_score = -1
    best_label = "C major"

    for root in range(12):
        for quality, intervals in _CHORD_TEMPLATES.items():
            template = set((root + i) % 12 for i in intervals)
            # Score = how many template tones are present, penalise missing tones
            hits = len(template & pitch_classes)
            score = hits / len(template)
            if score > best_score:
                best_score = score
                best_label = f"{_NOTE_NAMES[root]} {quality}"

    return best_label


def _tonic_chord(scale: str) -> str:
    """Returns tonic chord from scale string e.g. 'A minor' → 'A minor'."""
    # scale string is already 'Root quality' — tonic chord has same root and quality
    parts = scale.split()
    return f"{parts[0]} {'major' if parts[1] == 'major' else 'minor'}"
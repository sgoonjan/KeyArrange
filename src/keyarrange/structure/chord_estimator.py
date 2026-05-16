import logging
from keyarrange.dataclasses import Note

logger = logging.getLogger(__name__)

# Extra score added if the chord root is present in the bass — helps disambiguate between candidates with similar harmonic scores
BASS_BONUS = 0.33  # Set to be equivalent to exactly one additional chord tone match

# Chord quality intervals relative to root
_CHORD_TEMPLATES = {
    "major":      [0, 4, 7],
    "minor":      [0, 3, 7],
    "diminished": [0, 3, 6],
    "augmented":  [0, 4, 8],
}

_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

_DIATONIC_CHORDS = {
    "major": [
        (0, "major"), (2, "minor"), (4, "minor"),
        (5, "major"), (7, "major"), (9, "minor"), (11, "diminished")
    ],
    "minor": [
        (0, "minor"), (2, "diminished"), (3, "major"),
        (5, "minor"), (7, "minor"), (8, "major"), (10, "major")
    ]
}


def estimate_chords(
    other_notes: list[Note],
    bass_notes: list[Note],
    beat_times: list[float],
    scale: str,
) -> list[tuple[str, float]]:
    """Returns list of (chord_label, beat_time) e.g. [('C major', 0.0), ('G major', 1.2)]."""
    candidates = _candidates_for_scale(scale)
    chords = []

    for i, beat_start in enumerate(beat_times):
        beat_end = beat_times[i + 1] if i + 1 < len(beat_times) else beat_start + 0.5

        other_pcs = set()
        for n in other_notes:
            if n.start < beat_end and (n.start + n.duration) > beat_start:
                other_pcs.add(n.pitch % 12)

        bass_pcs = set()
        for n in bass_notes:
            if n.start < beat_end and (n.start + n.duration) > beat_start:
                bass_pcs.add(n.pitch % 12)

        if not other_pcs and not bass_pcs:
            label = chords[-1][0] if chords else _tonic_chord(scale)
        else:
            label = _best_chord(other_pcs, bass_pcs, candidates)

        chords.append((label, beat_start))

    return chords


def _candidates_for_scale(scale: str) -> list[tuple[int, str]]:
    # Returns (root_pitch_class, quality) pairs diatonic to the scale
    parts = scale.split()
    root_pc = _NOTE_NAMES.index(parts[0])
    mode = parts[1]  # "major" or "minor"
    return [((root_pc + interval) % 12, quality)
            for interval, quality in _DIATONIC_CHORDS[mode]]


def _best_chord(other_pcs: set[int], bass_pcs: set[int], candidates: list[tuple[int, str]]) -> str:
    best_score = -1
    best_label = "C major"
    for root, quality in candidates:
        template = set((root + i) % 12 for i in _CHORD_TEMPLATES[quality])
        harmonic_score = len(template & other_pcs) / len(template) if other_pcs else 0
        bass_bonus = BASS_BONUS if root in bass_pcs else 0
        score = harmonic_score + bass_bonus
        if score > best_score:
            best_score = score
            best_label = f"{_NOTE_NAMES[root]} {quality}"
    return best_label


def _tonic_chord(scale: str) -> str:
    """Returns tonic chord from scale string e.g. 'A minor' → 'A minor'."""
    # scale string is already 'Root quality' — tonic chord has same root and quality
    parts = scale.split()
    return f"{parts[0]} {'major' if parts[1] == 'major' else 'minor'}"
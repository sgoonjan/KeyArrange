import logging
from keyarrange.dataclasses import Note

logger = logging.getLogger(__name__)


NOTE_TO_PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
MAJOR_SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]


def filter_pitch_outliers(
    notes: list[Note],
    key: str,
    semitone_radius: int = 12,
    isolation_window: float = 0.5,
) -> list[Note]:
    """Drop notes that are statistical outliers OR chromatic+isolated."""
    if not notes:
        return notes
    
    key_pitch_classes = get_key_pitch_classes(key)

    pitches = sorted(n.pitch for n in notes)
    median_pitch = pitches[len(pitches) // 2]

    def _is_outlier(note: Note) -> bool:
        # Criterion 1: too far from the pitch centre of mass
        if abs(note.pitch - median_pitch) > semitone_radius:
            return True
        # Criterion 2: chromatic AND no diatonic neighbours nearby
        if note.pitch % 12 not in key_pitch_classes:
            has_diatonic_neighbour = any(
                n is not note
                and abs(n.start - note.start) <= isolation_window
                and n.pitch % 12 in key_pitch_classes
                for n in notes
            )
            if not has_diatonic_neighbour:
                return True
        return False

    return [n for n in notes if not _is_outlier(n)]


def get_key_pitch_classes(key: str) -> set[int]:
    """Returns set of pitch classes in the key e.g. {0, 2, 4, 5, 7, 9, 11} for C major."""
    tonic = key.split()[0]
    mode = key.split()[1]

    root_pc = NOTE_TO_PC[tonic]
    if mode == "major":
        return {(root_pc + interval) % 12 for interval in MAJOR_SCALE_INTERVALS}
    else: # minor
        return {(root_pc + interval) % 12 for interval in MINOR_SCALE_INTERVALS}
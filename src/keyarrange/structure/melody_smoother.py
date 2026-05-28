from keyarrange.dataclasses import Note


def smooth_melody(
    notes: list[Note],
    bpm: float,
    confidence_threshold: int = 55,
    ioi_multiplier: float = 1.0,
) -> list[Note]:
    """
    Two-pass filter: drop low-confidence notes, then drop notes
    that onset too quickly after the previous kept note.
    Basic Pitch encodes amplitude/confidence in velocity (0-127).
    """
    if not notes:
        return notes

    # Pass 1: confidence — Basic Pitch velocity reflects transcription confidence
    notes = [n for n in notes if n.velocity >= confidence_threshold]

    # Pass 2: inter-onset interval — drop notes faster than one 16th note
    min_ioi = (60 / bpm / 4) * ioi_multiplier  # one 16th note in seconds
    notes = sorted(notes, key=lambda n: n.start)

    kept: list[Note] = []
    for note in notes:
        if not kept:
            kept.append(note)
            continue
        ioi = note.start - kept[-1].start
        if ioi >= min_ioi:
            kept.append(note)
        elif note.velocity > kept[-1].velocity:
            # If the new note is more confident, prefer it
            kept[-1] = note

    return kept
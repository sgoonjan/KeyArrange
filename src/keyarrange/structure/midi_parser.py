import os
import sys
import pretty_midi
from keyarrange.dataclasses import Note

def load_midi(path: str, hand: str) -> list[Note]:
    """
    Extracts note information from MIDI file into a list of Note dataclasses.
    """
    if hand not in ['right', 'left']:
        raise ValueError("hand must be either 'right' or 'left'")

    if not os.path.exists(path):
        raise FileNotFoundError(f"MIDI file not found at {path}")

    midi_data = pretty_midi.PrettyMIDI(path)

    notes: list[Note] = []
    for instrument in midi_data.instruments:
        for pm_note in instrument.notes:
            notes.append(Note(
                pitch=pm_note.pitch,
                start=pm_note.start,
                end=pm_note.end,
                velocity=pm_note.velocity,
                hand=hand
            ))

    if not notes:
        raise ValueError('No notes found in MIDI file')

    notes.sort(key=lambda note: note.start) # Ordered for easier processing

    return notes


if __name__ == "__main__":
    result = load_midi(sys.argv[1], sys.argv[2])
    print(len(result))
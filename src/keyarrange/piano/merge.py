import pretty_midi
import os
import sys
from keyarrange.dataclasses import Note

def merge_tracks(right: list[Note], left: list[Note], output_file: str, bpm: float) -> None:
    if not right and not left:
        raise ValueError('No notes to merge')

    midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)

    right_hand_instrument = pretty_midi.Instrument(program=0, name='Right Hand')
    left_hand_instrument = pretty_midi.Instrument(program=0, name='Left Hand')

    for note in right:
        if note.start >= note.end:
            print(f"Warning: Skipping right hand note with start time ({note.start}) >= end time ({note.end})", file=sys.stderr)
            continue
        right_hand_instrument.notes.append(pretty_midi.Note(velocity=note.velocity, pitch=note.pitch, start=note.start, end=note.end))

    for note in left:
        if note.start >= note.end:
            print(f"Warning: Skipping left hand note with start time ({note.start}) >= end time ({note.end})", file=sys.stderr)
            continue
        left_hand_instrument.notes.append(pretty_midi.Note(velocity=note.velocity, pitch=note.pitch, start=note.start, end=note.end))

    midi.instruments.append(right_hand_instrument)
    midi.instruments.append(left_hand_instrument)

    midi.write(output_file)
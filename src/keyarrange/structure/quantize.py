
import numpy as np
from keyarrange.dataclasses import Note

def quantize_to_beats(notes: list[Note], beat_times: np.ndarray) -> list[Note]:
    if beat_times.size == 0:
        raise ValueError("beat_times cannot be empty.")

    quantized_notes = []
    for note in notes:
        nearest_beat_index = np.argmin(np.abs(beat_times - note.start))
        new_start = beat_times[nearest_beat_index]
        
        new_end = new_start + note.duration
        
        quantized_note = Note(
            start=new_start,
            end=new_end,
            pitch=note.pitch,
            velocity=note.velocity,
            hand=note.hand,
        )
        quantized_notes.append(quantized_note)

    return quantized_notes

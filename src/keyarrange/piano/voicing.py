from keyarrange.dataclasses import Note
import random


def _nearest_beat_index(time: float, beat_times: list[float]) -> int:
    # Returns index of closest beat to a given time
    return min(range(len(beat_times)), key=lambda i: abs(beat_times[i] - time))


def apply_velocity_curve(notes: list[Note], beat_times: list[float]) -> list[Note]:
    # Beat-strength velocity: downbeats loud, weak beats soft, humanized
    result = []
    for note in notes:
        beat_index = _nearest_beat_index(note.start, beat_times)
        
        if beat_index % 4 == 0:
            base_velocity = 90      # downbeat
        elif beat_index % 2 == 0:
            base_velocity = 75      # beat 3
        else:
            base_velocity = 60      # weak beats
        
        humanized = base_velocity + random.randint(-10, 10)
        velocity = max(30, min(110, humanized))  # clamp to sensible piano range
        
        result.append(Note(id=note.id, pitch=note.pitch, start=note.start, end=note.end, velocity=velocity, hand=note.hand))
    
    return result


def correct_octave(notes: list[Note], target_min: int = 48) -> list[Note]:
    # Transpose left hand up if it's sitting in bass guitar range
    if not notes:
        return notes
    
    median_pitch = sorted(n.pitch for n in notes)[len(notes) // 2]
    
    octaves_up = 0
    while median_pitch + (octaves_up * 12) < target_min:
        octaves_up += 1
    
    if octaves_up == 0:
        return notes
    
    shift = octaves_up * 12
    return [Note(id=n.id, pitch=min(n.pitch + shift, 127), start=n.start, end=n.end, velocity=n.velocity, hand=n.hand) for n in notes]



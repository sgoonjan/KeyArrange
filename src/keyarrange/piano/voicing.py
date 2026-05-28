from keyarrange.dataclasses import Note
import random


def _nearest_beat_index(time: float, beat_times: list[float]) -> int:
    # Returns index of closest beat to a given time
    return min(range(len(beat_times)), key=lambda i: abs(beat_times[i] - time))


def apply_velocity_curve(notes: list[Note], beat_times: list[float], role: str = "right") -> list[Note]:
    # Beat-strength velocity: downbeats loud, weak beats soft, humanized
    if role == "right":
        velocities = {0: 90, 2: 75, "weak": 60}
    else:
        velocities = {0: 65, 2: 50, "weak": 40}
    result = []
    for note in notes:
        beat_index = _nearest_beat_index(note.start, beat_times)
        
        if beat_index % 4 == 0:
            base_velocity = velocities[0]       # downbeat
        elif beat_index % 2 == 0:
            base_velocity = velocities[2]       # beat 3
        else:
            base_velocity = velocities["weak"]  # weak beats
        
        humanized = base_velocity + random.randint(-8, 8)  # Add some random variation for a more human feel
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


def generate_left_hand(
    chords: list[tuple[str, float]],
    beat_times: list[float],
    bpm: float,
) -> list[Note]:
    """Generate left hand notes from chord labels — root+third+fifth per beat."""
    _INTERVALS = {"major": [0, 4, 7], "minor": [0, 3, 7], "diminished": [0, 3, 6], "augmented": [0, 4, 8]}
    _NOTE_OFFSETS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}

    beat_duration = 60.0 / bpm
    notes = []
    note_id = 0

    for chord_label, beat_time in chords:
        parts = chord_label.split()
        root_name, quality = parts[0], parts[1]

        root_pc = _NOTE_OFFSETS.get(root_name, 0)
        intervals = _INTERVALS.get(quality, [0, 4, 7])

        root_midi = 48 + root_pc
        if root_midi > 60:
            root_midi -= 12

        for interval in intervals:
            notes.append(Note(
                id=note_id,
                pitch=root_midi + interval,
                start=beat_time,
                end=beat_time + beat_duration * 0.9,
                velocity=70, # Reasonable default, to be updated by velocity curve later
                hand="left",
            ))
            note_id += 1

    return notes
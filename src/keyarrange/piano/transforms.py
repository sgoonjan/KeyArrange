from keyarrange.dataclasses import Note

def _group_by_onset(notes: list[Note], window_ms: float = 50.0) -> list[list[Note]]:
    sorted_notes = sorted(notes, key=lambda note: note.start)
    groups: list[list[Note]] = []

    if not sorted_notes:
        return groups

    current_group: list[Note] = []
    window_seconds = window_ms / 1000.0

    for note in sorted_notes:
        if not current_group or (note.start - current_group[0].start) <= window_seconds:
            current_group.append(note)
        else:
            groups.append(current_group)
            current_group = [note]
    
    if current_group:
        groups.append(current_group)

    return groups

def density_reducer(notes: list[Note], bpm: float, multiplier: int = 1) -> list[Note]:
    window_duration = 0.5  # 500ms
    step_size = 0.25  # 250ms
    dropped_note_ids = set()

    notes.sort(key=lambda note: note.start)

    last_note_start_time = 0.0
    if notes:
        last_note_start_time = max(note.start for note in notes)

    t = 0.0
    while t <= last_note_start_time + window_duration: # Extend windowing slightly past the last note's start time
        window_notes = [note for note in notes if t <= note.start < t + window_duration and note.id not in dropped_note_ids]

        max_notes_in_window = max(1, int(120 / bpm)) * multiplier

        if len(window_notes) > max_notes_in_window:
            # Sort by duration (longest first) and keep only the top `max_notes_in_window`
            window_notes.sort(key=lambda note: note.duration, reverse=True)
            notes_to_drop = window_notes[max_notes_in_window:]

            for note in notes_to_drop:
                dropped_note_ids.add(note.id)

        t += step_size

    return [note for note in notes if note.id not in dropped_note_ids]

def span_enforcer(notes: list[Note], max_span: int = 12, hand: str = "right") -> list[Note]:
    processed_notes: list[Note] = []
    
    onset_groups = _group_by_onset(notes)

    for group in onset_groups:
        current_group = sorted(group, key=lambda note: note.pitch)

        while len(current_group) > 1 and (current_group[-1].pitch - current_group[0].pitch) > max_span:
            if hand == "right":
                # For right hand, drop the lowest pitch note to reduce span
                current_group.pop(0)
            elif hand == "left":
                # For left hand, drop the highest pitch note to reduce span
                current_group.pop(-1)
            else:
                # Should not happen with valid input, but as a safeguard
                break
        processed_notes.extend(current_group)

    return processed_notes

def note_cap(notes: list[Note], max_notes: int = 3) -> list[Note]:
    processed_notes: list[Note] = []
    
    onset_groups = _group_by_onset(notes)

    for group in onset_groups:
        current_group = sorted(group, key=lambda note: note.duration)

        while len(current_group) > max_notes:
            current_group.pop(0)  # Drop the shortest duration note
        processed_notes.extend(current_group)

    return processed_notes

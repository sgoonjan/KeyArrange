import librosa
import numpy as np
import sys
import os
from keyarrange.dataclasses import Note


def get_beat_times(audio_path: str) -> tuple[np.ndarray, float]:
    """
    Uses librosa to analyze the audio file to extract beat times and BPM.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at: {audio_path}")

    y, sr = librosa.load(audio_path, mono=True)

    bpm, beat_times = librosa.beat.beat_track(y=y, sr=sr, units='time')

    if beat_times.size == 0:
        raise ValueError("No beats detected in the audio file.")

    return beat_times, bpm


def assign_beat_strength(notes: list[Note], beat_times: np.ndarray, window: float = 0.1) -> list[Note]:
    """Tag each note with is_on_beat using existing librosa beat times."""
    for note in notes:
        note.is_on_beat = bool(
            np.any(np.abs(beat_times - note.start) <= window)
        )
    return notes


if __name__ == "__main__":
    res_1, res_2 = get_beat_times(sys.argv[1])
    print(len(res_1))
    print(res_2)

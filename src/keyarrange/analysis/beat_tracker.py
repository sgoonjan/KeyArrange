import librosa
import numpy as np
import sys
import os

def get_beat_times(audio_path: str) -> tuple[np.ndarray, float]:
    """
    Uses librosa to analyze the audio file to extract beat times and BPM.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at: {audio_path}")

    y, sr = librosa.load(audio_path, mono=True)

    beat_times, bpm = librosa.beat.beat_track(y=y, sr=sr, units='time')

    if beat_times.size == 0:
        raise ValueError("No beats detected in the audio file.")

    return beat_times, bpm


if __name__ == "__main__":
    res_1, res_2 = get_beat_times(sys.argv[1])
    print(res_1)
    print(res_2)

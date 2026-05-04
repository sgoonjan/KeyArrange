import logging
import numpy as np
import librosa

logger = logging.getLogger(__name__)

# Krumhansl-Schmuckler scale profiles — major then minor
_MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
_MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def get_scale(audio_path: str) -> str:
    """Returns scale string e.g. 'C major' or 'E minor'."""
    y, sr = librosa.load(audio_path, mono=True)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr).mean(axis=1)  # average over time → 12 values

    best_score = -np.inf
    best_scale = "C major"

    for root in range(12):
        rotated = np.roll(chroma, -root)  # align chroma so 'root' is at index 0
        
        major_score = np.corrcoef(rotated, _MAJOR_PROFILE)[0, 1]
        minor_score = np.corrcoef(rotated, _MINOR_PROFILE)[0, 1]

        if major_score > best_score:
            best_score = major_score
            best_scale = f"{_NOTE_NAMES[root]} major"
        if minor_score > best_score:
            best_score = minor_score
            best_scale = f"{_NOTE_NAMES[root]} minor"

    logger.info(f"Detected scale: {best_scale}")
    return best_scale
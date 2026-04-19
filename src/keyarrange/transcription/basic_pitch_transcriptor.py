import sys
from pathlib import Path
from basic_pitch.inference import predict

def transcribe_stem(audio_path: str, output_dir: str) -> Path:
    """
    Transcribe audio stem to MIDI using Basic Pitch.
    """
    audio_path = Path(audio_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    stem_name = audio_path.stem
    output_path = output_dir / f"{stem_name}_transcription.mid"

    print(f"Starting transcription for {audio_path.name}...")

    # Call predict with the string representation of the audio_path
    _, midi_data, _ = predict(
        str(audio_path)
    )

    # Save the PrettyMIDI object to the specified output path
    midi_data.write(str(output_path))

    print(f"Transcription complete. MIDI saved to {output_path}")

    return output_path

if __name__ == "__main__":
    output_path = transcribe_stem(sys.argv[1], sys.argv[2])
    print(f"Transcribed stem: {output_path}")
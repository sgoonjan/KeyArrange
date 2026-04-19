import subprocess
import sys
from pathlib import Path


def separate(audio_path: str, output_dir: str) -> dict[str, str]:
    """
    Run Demucs source separation on an audio file.
    
    Returns:
        Dictionary mapping stem names to absolute file paths
    
    Raises:
        RuntimeError: If expected stem files are missing after separation
    """
    audio_path = Path(audio_path).resolve()
    output_dir = Path(output_dir).resolve()
    
    # Run Demucs separation
    subprocess.run(
        ["python", "-m", "demucs", "-n", "htdemucs", "--out", str(output_dir), str(audio_path)],
        check=True
    )
    
    # Demucs creates nested structure: {output_dir}/htdemucs/{song_name}/
    song_name = audio_path.stem
    stems_base = output_dir / "htdemucs" / song_name
    
    # Locate all four expected stems
    expected_stems = ["vocals", "bass", "drums", "other"]
    stem_paths = {}
    missing_stems = []
    
    for stem in expected_stems:
        stem_file = stems_base / f"{stem}.wav"
        if stem_file.exists():
            stem_paths[stem] = str(stem_file.resolve())
        else:
            missing_stems.append(stem)
    
    if missing_stems:
        raise RuntimeError(
            f"Missing stems after Demucs separation: {missing_stems}. "
            f"Looked in: {stems_base}"
        )
    
    return stem_paths


if __name__ == "__main__":
    result = separate(sys.argv[1], sys.argv[2])
    for stem, path in result.items():
        print(f"{stem}: {path}")

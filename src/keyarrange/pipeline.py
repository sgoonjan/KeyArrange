"""Pipeline coordinator — owns directory structure and stage sequencing."""
import logging
from pathlib import Path

from keyarrange.separation.demucs_runner import separate

from keyarrange.transcription.basic_pitch_transcriptor import transcribe_stem

from keyarrange.analysis.beat_tracker import get_beat_times
from keyarrange.analysis.scale_detection import get_scale

from keyarrange.structure.midi_parser import load_midi
from keyarrange.structure.chord_estimator import estimate_chords

from keyarrange.piano.merge import merge_tracks
from keyarrange.piano.voicing import apply_velocity_curve, generate_left_hand
from keyarrange.piano.transforms import density_reducer, span_enforcer, note_cap

from keyarrange.render.piano_roll import render_piano_roll

logger = logging.getLogger(__name__)


class Pipeline:
    """Disk-based pipeline: each stage writes output before the next runs."""
    
    def __init__(self, input_path: str, output_dir: str):
        self.input_path = Path(input_path)
        
        if not self.input_path.exists():
            raise ValueError(f"Input file does not exist: {input_path}")
        
        song_name = self.input_path.stem
        base_dir = Path(output_dir) / song_name
        self.base_dir = base_dir
        
        self.stems_dir = base_dir / "stems"
        self.transcriptions_dir = base_dir / "transcriptions"
        self.arranged_dir = base_dir / "arranged"
        
        self.stems_dir.mkdir(parents=True, exist_ok=True)
        self.transcriptions_dir.mkdir(parents=True, exist_ok=True)
        self.arranged_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self) -> str:
        output_file_path = self.arranged_dir / "arranged.mid"
        piano_roll_path = self.arranged_dir / "piano_roll.png"

        logger.info("Running stem separation...")
        stem_paths = separate(str(self.input_path), str(self.stems_dir))
        vocals_audio_path = stem_paths["vocals"]
        bass_audio_path = stem_paths["bass"]

        logger.info("Transcribing vocal stem...")
        vocals_midi_path = transcribe_stem(vocals_audio_path, str(self.transcriptions_dir))

        logger.info("Transcribing bass stem...")
        bass_midi_path = transcribe_stem(bass_audio_path, str(self.transcriptions_dir))

        logger.info("Transcribing other stem...")
        other_midi_path = transcribe_stem(stem_paths["other"], str(self.transcriptions_dir))

        logger.info("Getting beat times...")
        beat_times, bpm = get_beat_times(str(self.input_path))

        logger.info("Detecting scale...")
        scale = get_scale(str(self.input_path))

        logger.info("Loading vocal MIDI...")
        right_notes = load_midi(str(vocals_midi_path), hand="right")

        logger.info("Loading bass MIDI...")
        left_notes = load_midi(str(bass_midi_path), hand="left")

        logger.info("Loading other stem MIDI...")
        other_notes = load_midi(str(other_midi_path), hand="left") # hand label irrelevant here

        logger.info("Estimating chords...")
        chords = estimate_chords(other_notes, beat_times, scale)

        logger.info("Generating chord-aware left hand...")
        left_notes = generate_left_hand(chords, beat_times, bpm)

        logger.info("Applying transformations to Right hand notes...")
        right_notes = density_reducer(right_notes, bpm, multiplier=2)  # Allow density relaxation for vocals
        right_notes = span_enforcer(right_notes, max_span=12, hand="right")
        right_notes = note_cap(right_notes, max_notes=3)
        right_notes = apply_velocity_curve(right_notes, beat_times)

        logger.info("Applying transformations to Left hand notes...")
        left_notes = density_reducer(left_notes, bpm)
        left_notes = span_enforcer(left_notes, max_span=12, hand="left")
        left_notes = note_cap(left_notes, max_notes=3)
        left_notes = apply_velocity_curve(left_notes, beat_times)

        logger.info("Merging tracks...")
        merge_tracks(right_notes, left_notes, str(output_file_path), bpm)

        logger.info("Rendering piano roll...")
        try:
            render_piano_roll(right_notes, left_notes, str(piano_roll_path))
        except Exception as e:
            logger.warning(f"Piano roll render failed ({e}), continuing without it")
            piano_roll_path = None

        logger.info(f"Pipeline complete: {output_file_path}")
        return str(output_file_path), str(piano_roll_path) if piano_roll_path else None
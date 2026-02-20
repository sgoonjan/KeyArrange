"""Pipeline coordinator — owns directory structure and stage sequencing."""

from pathlib import Path


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
    
    def run(self) -> dict:
        """Placeholder — will be implemented once stage modules exist."""
        print("Pipeline.run() not yet implemented")
        return {}

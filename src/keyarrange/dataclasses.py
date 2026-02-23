from dataclasses import dataclass

@dataclass
class Note:
    pitch: int
    start: float
    end: float
    velocity: int
    hand: str  # 'right' or 'left'

    @property
    def duration(self) -> float:
        return self.end - self.start
    


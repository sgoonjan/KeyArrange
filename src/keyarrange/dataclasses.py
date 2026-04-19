from dataclasses import dataclass

@dataclass
class Note:
    id: int
    pitch: int
    start: float
    end: float
    velocity: int
    hand: str  # 'right' or 'left'

    @property
    def duration(self) -> float:
        return self.end - self.start
    


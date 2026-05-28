from dataclasses import dataclass, field

@dataclass
class Note:
    id: int
    pitch: int
    start: float
    end: float
    velocity: int
    hand: str  # 'right' or 'left'
    is_on_beat: bool = field(default=False, compare=False) # compare=False: beat assignment is derived, not part of note identity

    @property
    def duration(self) -> float:
        return self.end - self.start
    


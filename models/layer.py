from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from models.base import BaseModel


@dataclass
class AELayer(BaseModel):
    """Model warstwy After Effects"""
    name: str
    index: int
    type: str
    enabled: bool
    solo: bool
    shy: bool
    in_point: float
    out_point: float
    start_time: float
    stretch: float
    quality: str
    source_name: Optional[str] = None
    source_path: Optional[str] = None
    effects: List[Dict[str, Any]] = field(default_factory=list)
    markers: List[Dict[str, Any]] = field(default_factory=list)
    parent: Optional[str] = None
    blending_mode: str = "normal"
    three_d_layer: bool = False
    preserve_transparency: bool = False

    def add_effect(self, effect: Dict[str, Any]) -> None:
        """Dodaje efekt do warstwy"""
        self.effects.append(effect)

    def print_summary(self) -> None:
        """Wyświetla podsumowanie warstwy"""
        print(f"    - {self.name} ({self.type})")
        if self.source_path:
            print(f"      Źródło: {self.source_path}")
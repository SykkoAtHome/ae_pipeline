from dataclasses import dataclass, field
from typing import List, Dict, Any
from layer import AELayer
from models.base import BaseModel


@dataclass
class AEComposition(BaseModel):
    """Model kompozycji After Effects"""
    name: str
    id: str
    duration: float
    frame_rate: float
    width: int
    height: int
    pixel_aspect: float
    background_color: str
    work_area_start: float
    work_area_duration: float
    layers: List[AELayer] = field(default_factory=list)
    markers: List[Dict[str, Any]] = field(default_factory=list)

    def add_layer(self, layer: AELayer) -> None:
        """Dodaje warstwę do kompozycji"""
        self.layers.append(layer)

    def print_summary(self) -> None:
        """Wyświetla podsumowanie kompozycji"""
        print(f"\n- {self.name}")
        print(f"  Wymiary: {self.width}x{self.height}")
        print(f"  FPS: {self.frame_rate}")
        print(f"  Czas trwania: {self.duration}")
        print(f"  Liczba warstw: {len(self.layers)}")
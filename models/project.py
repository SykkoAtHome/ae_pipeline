from dataclasses import dataclass, field
from typing import List, Dict, Any

from .base import BaseModel
from .composition import AEComposition
from .footage import AEFootage

@dataclass
class AEProject(BaseModel):
    """Model projektu After Effects"""
    name: str
    path: str
    version: str
    frame_rate: float
    width: int
    height: int
    duration: float
    bits_per_channel: int
    working_color_space: str
    expression_engine: str
    compositions: List[AEComposition] = field(default_factory=list)
    footage: List[AEFootage] = field(default_factory=list)
    folders: List[Dict[str, Any]] = field(default_factory=list)

    def add_composition(self, composition: AEComposition) -> None:
        """Dodaje kompozycję do projektu"""
        self.compositions.append(composition)

    def add_footage(self, footage: AEFootage) -> None:
        """Dodaje footage do projektu"""
        self.footage.append(footage)

    def print_summary(self) -> None:
        """Wyświetla podsumowanie projektu"""
        print(f"\nProjekt: {self.name}")
        print(f"Wersja AE: {self.version}")
        print(f"Wymiary: {self.width}x{self.height}")
        print(f"Frame Rate: {self.frame_rate}")
        print(f"\nKompozycje ({len(self.compositions)}):")
        for comp in self.compositions:
            comp.print_summary()
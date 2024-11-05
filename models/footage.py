from dataclasses import dataclass
from typing import Optional

from models.base import BaseModel


@dataclass
class AEFootage(BaseModel):
    """Model footage (materiału źródłowego) w After Effects"""
    name: str
    id: str
    path: str
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    pixel_aspect: float = 1.0
    has_video: bool = False
    has_audio: bool = False
    is_still: bool = False
    native_fps: Optional[float] = None
    field_order: Optional[str] = None
    alpha_mode: Optional[str] = None
    is_sequence: bool = False
    sequence_start: Optional[int] = None
    sequence_duration: Optional[float] = None
    sequence_frame_rate: Optional[float] = None

    def print_summary(self) -> None:
        """Wyświetla podsumowanie footage"""
        print(f"\n- {self.name}")
        if self.path:
            print(f"  Ścieżka: {self.path}")
        if self.width and self.height:
            print(f"  Wymiary: {self.width}x{self.height}")
        if self.duration:
            print(f"  Czas trwania: {self.duration}")
        if self.is_sequence:
            print(f"  Sekwencja: {self.sequence_frame_rate} FPS")
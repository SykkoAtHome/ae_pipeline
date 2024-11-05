from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class BaseModel:
    """Base class for all models"""

    def to_dict(self) -> Dict[str, Any]:
        """Converts object to dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

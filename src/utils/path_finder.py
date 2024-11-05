import os
from pathlib import Path


class AEPathFinder:
    """Class for managing After Effects paths"""

    AE_POSSIBLE_PATHS = [
        r"C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\AfterFX.exe",
        r"C:\Program Files\Adobe\Adobe After Effects 2023\Support Files\AfterFX.exe",
        r"C:\Program Files\Adobe\Adobe After Effects 2022\Support Files\AfterFX.exe"
    ]

    @classmethod
    def find_ae_executable(cls):
        """Finds path to After Effects executable"""
        for path in cls.AE_POSSIBLE_PATHS:
            if os.path.exists(path):
                return path
        raise FileNotFoundError("After Effects executable not found.")

    @staticmethod
    def get_temp_path(project_path: str, filename: str) -> str:
        """Generates path for temporary file"""
        project_dir = os.path.dirname(project_path)
        return os.path.join(project_dir, filename)

    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalizes path for use in JSX scripts"""
        return path.replace('\\', '/')
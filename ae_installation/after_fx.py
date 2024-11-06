import os
from pathlib import Path
import win32api
from typing import Optional, Dict, List


class AfterFX:
    DEFAULT_SEARCH_PATHS = [
        r"C:\Program Files\Adobe",
        r"C:\Program Files (x86)\Adobe"
    ]

    def __init__(self, search_paths: Optional[List[str]] = None):
        """
        Initialize AE installation checker
        Args:
            search_paths (List[str], optional): List of paths where to search for AE installations.
                                              If None, will use default paths.
        """
        self.search_paths = [Path(p) for p in (search_paths or self.DEFAULT_SEARCH_PATHS)]
        self.found_installations = self._find_ae_installations()

    def _find_ae_installations(self) -> List[Path]:
        """Find all AfterFX.exe files in specified search paths"""
        found_exes = []

        for base_path in self.search_paths:
            if not base_path.exists():
                continue

            for exe_path in base_path.rglob("AfterFX.exe"):
                if exe_path.exists():
                    found_exes.append(exe_path)

        return found_exes

    def _get_file_info(self, exe_path: Path, info: dict, name: str) -> str:
        """Helper to get string file info"""
        try:
            lang, codepage = win32api.GetFileVersionInfo(str(exe_path), '\\VarFileInfo\\Translation')[0]
            string_file_info = f'\\StringFileInfo\\{lang:04x}{codepage:04x}\\{name}'
            return win32api.GetFileVersionInfo(str(exe_path), string_file_info)
        except:
            return "Unknown"

    def _clean_path(self, path: Path) -> str:
        """Convert path to raw string with single backslashes"""
        return str(path).replace('\\\\', '\\')

    def _get_installation_info(self, exe_path: Path) -> Optional[dict]:
        """Get version information for a single installation"""
        try:
            info = win32api.GetFileVersionInfo(str(exe_path), "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"

            return {
                "product_name": self._get_file_info(exe_path, info, 'ProductName'),
                "path": self._clean_path(exe_path.parent.parent),
                "exe_path": self._clean_path(exe_path),
                "version": version,
                "product_version": self._get_file_info(exe_path, info, 'ProductVersion')
            }
        except:
            return None

    def get_all_versions(self) -> List[dict]:
        """Get information about all found AE installations"""
        installations = []

        for exe_path in self.found_installations:
            info = self._get_installation_info(exe_path)
            if info:
                installations.append(info)

        return installations
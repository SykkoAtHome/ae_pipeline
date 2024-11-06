import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict
import re
import os
from datetime import datetime


@dataclass
class AEVersion:
    full_version: str
    year: str
    version: str
    platform: str
    build: int
    is_beta: bool = False

    @staticmethod
    def parse_version_string(version_str: str, build: int) -> 'AEVersion':
        pattern = r"(\d{4}),\s+v([\d.]+)\s*(BETA)?\s*\((.*?)\)"
        match = re.match(pattern, version_str)

        if not match:
            return AEVersion(
                full_version="Unknown",
                year="Unknown",
                version="Unknown",
                platform="Unknown",
                build=build
            )

        year, version, beta, platform = match.groups()
        return AEVersion(
            full_version=version_str,
            year=year,
            version=version,
            platform=platform,
            build=build,
            is_beta=bool(beta)
        )

    def to_dict(self) -> dict:
        return asdict(self)


class AEProjectFile:
    START_HEADER = b'\x68\x65\x61\x64'
    BUFFER_SIZE = 40

    def __init__(self, project_path: str):
        self.project_path = self._process_path(project_path)
        self.version_map = self._load_version_signatures()

        if self.project_path.suffix.lower() != '.aep':
            raise ValueError("File must have .aep extension")

    def _format_date(self, timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    def _process_path(self, path: str) -> Path:
        try:
            clean_path = path.replace('\x00', '').strip()

            if os.name == 'nt':
                clean_path = clean_path.replace('/', '\\')

            abs_path = os.path.abspath(clean_path)
            path_obj = Path(abs_path)

            if not path_obj.exists():
                raise FileNotFoundError(f"Project file not found: {abs_path}")

            return path_obj

        except Exception as e:
            raise

    def _load_version_signatures(self) -> Dict[bytes, str]:
        try:
            json_path = Path(__file__).parent / 'ae-builds.json'
            with open(json_path, 'r') as f:
                json_data = json.load(f)
            return {bytes.fromhex(item['hex']): item['version'] for item in json_data}
        except Exception:
            return {}

    def _get_file_info(self) -> dict:
        try:
            stats = os.stat(self.project_path)
            return {
                "status": "success",
                "file_info": {
                    "path": str(self.project_path),
                    "size": stats.st_size,
                    "modified": self._format_date(stats.st_mtime),
                    "created": self._format_date(stats.st_ctime)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Cannot read file info: {str(e)}"
            }

    def get_version_info(self) -> dict:
        result = self._get_file_info()
        if result["status"] != "success":
            return result

        try:
            with open(self.project_path, 'rb') as f:
                buffer = f.read(self.BUFFER_SIZE)
                while buffer:
                    header_pos = buffer.find(self.START_HEADER)

                    if header_pos != -1:
                        version_signature = buffer[32:39]
                        build_number = buffer[39]
                        found_signature = version_signature.hex()

                        if version_signature in self.version_map:
                            version_str = self.version_map[version_signature]
                            result["version_status"] = "success"
                        else:
                            version_str = "Unknown"
                            result["version_status"] = "failed"

                        version_info = AEVersion.parse_version_string(version_str, build_number)

                        result["version_info"] = version_info.to_dict()
                        result["debug_info"] = {
                            "signature_hex": found_signature
                        }

                        return result

                    buffer = f.read(self.BUFFER_SIZE)

                result["version_status"] = "failed"
                result["version_info"] = AEVersion(
                    full_version="Unknown",
                    year="Unknown",
                    version="Unknown",
                    platform="Unknown",
                    build=0,
                    is_beta=False
                ).to_dict()
                result["debug_info"] = {
                    "signature_hex": None
                }
                return result

        except Exception as e:
            result["version_status"] = "error"
            result["message"] = str(e)
            return result
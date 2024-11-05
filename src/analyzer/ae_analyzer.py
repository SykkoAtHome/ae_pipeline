import os
import subprocess
import json
from typing import Optional

from src.utils.path_finder import AEPathFinder
from src.utils.logger import setup_logger
from jsx_generator import JSXGenerator
from parser import AEOutputParser
from models.project import AEProject



class AEAnalyzer:
    """Main class for analyzing After Effects projects"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.ae_path = AEPathFinder.find_ae_executable()

    def analyze_project(self, project_path: str) -> Optional[AEProject]:
        """Analyzes After Effects project"""
        if not project_path.endswith('.aep'):
            self.logger.error("Only .aep files are supported")
            return None

        try:
            # Prepare paths
            output_path = AEPathFinder.get_temp_path(project_path, "project_analysis.txt")
            jsx_path = AEPathFinder.get_temp_path(project_path, "temp_analysis.jsx")

            # Generate and save JSX script
            jsx_content = JSXGenerator.create_analysis_script(
                AEPathFinder.normalize_path(project_path),
                AEPathFinder.normalize_path(output_path)
            )

            with open(jsx_path, 'w', encoding='utf-8') as f:
                f.write(jsx_content)

            # Run After Effects
            self._run_after_effects(jsx_path)

            # Parse results
            if os.path.exists(output_path):
                with open(output_path, 'r', encoding='utf-8') as f:
                    if os.path.getsize(output_path) == 0:
                        self.logger.error("Output file is empty")
                        return None

                raw_data = AEOutputParser.parse_file(output_path)
                if raw_data:
                    project = AEOutputParser.create_project(raw_data)
                    self._save_json_report(project, project_path)
                    return project

            self.logger.error("Output file not found or parsing failed")
            return None

        except subprocess.TimeoutExpired:
            self.logger.error("After Effects process timed out")
            return None
        except Exception as e:
            self.logger.exception(f"Error during analysis: {str(e)}")
            return None
        finally:
            self._cleanup_temp_files(jsx_path, output_path)

    def _run_after_effects(self, jsx_path: str) -> None:
        """Runs After Effects with JSX script"""
        cmd = [
            self.ae_path,
            "-noui",
            "-r", jsx_path
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for process to complete
        try:
            stdout, stderr = process.communicate(timeout=30)
            if process.returncode != 0:
                self.logger.error(f"After Effects process failed: {stderr.decode()}")
        except subprocess.TimeoutExpired:
            process.kill()
            raise

    def _save_json_report(self, project: AEProject, original_path: str) -> None:
        """Saves report in JSON format"""
        try:
            json_path = os.path.join(
                os.path.dirname(original_path),
                f"{os.path.splitext(os.path.basename(original_path))[0]}_analysis.json"
            )
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, indent=2, ensure_ascii=False)

            self.logger.info(f"Analysis report saved to: {json_path}")
        except Exception as e:
            self.logger.error(f"Failed to save JSON report: {str(e)}")

    def _cleanup_temp_files(self, *files) -> None:
        """Removes temporary files"""
        for file in files:
            if file and os.path.exists(file):
                try:
                    os.remove(file)
                except Exception as e:
                    self.logger.warning(f"Failed to remove temp file {file}: {str(e)}")
import os
import subprocess
import json
import time
from pathlib import Path
import logging


class AECommandLineAnalyzer:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        possible_paths = [
            r"C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\AfterFX.exe",
            r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\AfterFX.exe",
        ]

        self.afterfx_path = None
        for path in possible_paths:
            if os.path.exists(path):
                self.afterfx_path = path
                break

        if not self.afterfx_path:
            raise Exception("Nie znaleziono After Effects.")

    def create_analysis_script(self, project_path, output_path):
        project_path = project_path.replace('\\', '/')
        output_path = output_path.replace('\\', '/')

        jsx_content = f'''
        var logFile = new File("{output_path}.log");
        logFile.open("w");

        function writeLog(msg) {{
            logFile.write(msg + "\\n");
            logFile.close();
            logFile.open("a");
        }}

        writeLog("Script started");

        try {{
            writeLog("Opening project");
            var project = app.open(File("{project_path}"));

            var output_file = new File("{output_path}");
            output_file.open("w");

            // Zapisz podstawowe informacje o projekcie
            output_file.writeln("PROJECT_INFO_START");
            output_file.writeln("name=" + project.file.name);
            output_file.writeln("path=" + project.file.fsName);
            output_file.writeln("numItems=" + project.numItems);
            output_file.writeln("PROJECT_INFO_END");

            // Zapisz informacje o kompozycjach
            output_file.writeln("COMPOSITIONS_START");
            for (var i = 1; i <= project.numItems; i++) {{
                var item = project.item(i);
                if (item instanceof CompItem) {{
                    output_file.writeln("COMP_START");
                    output_file.writeln("name=" + item.name);
                    output_file.writeln("duration=" + item.duration);
                    output_file.writeln("frameRate=" + item.frameRate);
                    output_file.writeln("width=" + item.width);
                    output_file.writeln("height=" + item.height);
                    output_file.writeln("numLayers=" + item.numLayers);
                    output_file.writeln("COMP_END");
                }}
            }}
            output_file.writeln("COMPOSITIONS_END");

            // Zapisz informacje o footage
            output_file.writeln("FOOTAGE_START");
            for (var i = 1; i <= project.numItems; i++) {{
                var item = project.item(i);
                if (item instanceof FootageItem) {{
                    output_file.writeln("FOOTAGE_ITEM_START");
                    output_file.writeln("name=" + item.name);
                    if (item.file) {{
                        output_file.writeln("file=" + item.file.fsName);
                    }}
                    output_file.writeln("FOOTAGE_ITEM_END");
                }}
            }}
            output_file.writeln("FOOTAGE_END");

            // Zapisz informacje o folderach
            output_file.writeln("FOLDERS_START");
            for (var i = 1; i <= project.numItems; i++) {{
                var item = project.item(i);
                if (item instanceof FolderItem) {{
                    output_file.writeln("FOLDER_START");
                    output_file.writeln("name=" + item.name);
                    output_file.writeln("numItems=" + item.numItems);
                    output_file.writeln("FOLDER_END");
                }}
            }}
            output_file.writeln("FOLDERS_END");

            output_file.close();
            writeLog("Analysis completed");

            project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
            writeLog("Project closed");

            app.quit();
        }} catch (e) {{
            writeLog("Error occurred: " + e.toString());
            if (logFile) logFile.close();
            app.quit();
        }}
        '''

        jsx_path = os.path.join(os.path.dirname(project_path), "temp_analysis.jsx")
        with open(jsx_path, 'w', encoding='utf-8') as f:
            f.write(jsx_content)

        self.logger.debug(f"Created JSX script at: {jsx_path}")
        return jsx_path

    def parse_output_file(self, file_path):
        """Parsuje plik wyjściowy do formatu JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            result = {
                'project_info': {},
                'compositions': [],
                'footage': [],
                'folders': []
            }

            current_section = None
            current_item = None

            for line in lines:
                line = line.strip()

                if line == 'PROJECT_INFO_START':
                    current_section = 'project_info'
                elif line == 'COMPOSITIONS_START':
                    current_section = 'compositions'
                elif line == 'FOOTAGE_START':
                    current_section = 'footage'
                elif line == 'FOLDERS_START':
                    current_section = 'folders'
                elif line in ['COMP_START', 'FOOTAGE_ITEM_START', 'FOLDER_START']:
                    current_item = {}
                elif line in ['COMP_END', 'FOOTAGE_ITEM_END', 'FOLDER_END']:
                    if current_section == 'compositions':
                        result['compositions'].append(current_item)
                    elif current_section == 'footage':
                        result['footage'].append(current_item)
                    elif current_section == 'folders':
                        result['folders'].append(current_item)
                    current_item = None
                elif '=' in line:
                    key, value = line.split('=', 1)
                    if current_item is not None:
                        current_item[key] = value
                    elif current_section == 'project_info':
                        result['project_info'][key] = value

            return result

        except Exception as e:
            self.logger.error(f"Error parsing output file: {str(e)}")
            return None

    def analyze_project(self, project_path):
        try:
            self.logger.info(f"Starting analysis of: {project_path}")

            project_dir = os.path.dirname(project_path)
            output_path = os.path.join(project_dir, "project_analysis.txt")
            log_path = output_path + ".log"
            jsx_path = self.create_analysis_script(project_path, output_path)

            cmd = [
                self.afterfx_path,
                "-noui",
                "-r", jsx_path
            ]

            self.logger.info("Starting After Effects process...")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )

            # Czekaj na utworzenie pliku
            start_time = time.time()
            while time.time() - start_time < 30:
                if os.path.exists(output_path):
                    time.sleep(1)  # Daj czas na dokończenie zapisu
                    results = self.parse_output_file(output_path)
                    if results:
                        # Zapisz jako JSON
                        json_path = output_path.replace('.txt', '.json')
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(results, f, indent=2)
                        self.logger.info(f"Results saved to {json_path}")
                        return results
                time.sleep(1)
                print(".", end="", flush=True)

            self.logger.error("Timeout waiting for analysis results")
            return None

        except Exception as e:
            self.logger.exception("Error during analysis")
            return None
        finally:
            # Cleanup
            for file in [jsx_path, output_path, log_path]:
                if os.path.exists(file):
                    os.remove(file)


def main():
    project_path = r"A:\__ORYGINAL_POST__\GSK\SENSODYNE_2\SENSODYNE_NOUSISH_20\02_PROJECT\SENSODYNE_NOUSISH_20s_v2.aep"
    project_path = os.path.abspath(project_path)

    analyzer = AECommandLineAnalyzer()
    print(f"Znaleziono After Effects w: {analyzer.afterfx_path}")
    print(f"Rozpoczynam analizę projektu: {project_path}")

    results = analyzer.analyze_project(project_path)

    if results:
        print("\nAnaliza zakończona pomyślnie!")
        print(f"\nInformacje o projekcie:")
        for key, value in results['project_info'].items():
            print(f"- {key}: {value}")

        print(f"\nZnalezione elementy:")
        print(f"- Kompozycje: {len(results['compositions'])}")
        print(f"- Footage: {len(results['footage'])}")
        print(f"- Foldery: {len(results['folders'])}")

        print("\nKompozycje:")
        for comp in results['compositions']:
            print(f"- {comp['name']} ({comp['width']}x{comp['height']} @ {comp['frameRate']}fps)")
    else:
        print("\nNie udało się wykonać analizy.")


if __name__ == "__main__":
    main()

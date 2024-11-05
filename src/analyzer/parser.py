from typing import Dict, Optional

from models.composition import AEComposition
from models.footage import AEFootage
from models.layer import AELayer
from models.project import AEProject


class AEOutputParser:
    """Parser for After Effects project analysis output"""

    @staticmethod
    def parse_file(file_path: str) -> Optional[Dict]:
        """
        Parses output file into data structure

        Args:
            file_path: Path to analysis output file

        Returns:
            Dictionary containing parsed data or None if parsing failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()]

            result = {
                'project_info': {},
                'compositions': [],
                'footage': [],
                'folders': []
            }

            section = None
            current_item = None
            current_layer = None

            for line in lines:
                if not line:
                    continue

                # Project info section
                if line == "PROJECT_INFO_START":
                    section = "project_info"
                    continue
                elif line == "PROJECT_INFO_END":
                    section = None
                    continue

                # Compositions section
                elif line == "COMPOSITIONS_START":
                    section = "compositions"
                    continue
                elif line == "COMPOSITIONS_END":
                    section = None
                    continue

                # Single composition
                elif line == "COMP_START":
                    current_item = {'layers': []}
                    continue
                elif line == "COMP_END":
                    result['compositions'].append(current_item)
                    current_item = None
                    continue

                # Layers section
                elif line == "LAYERS_START":
                    section = "layers"
                    continue
                elif line == "LAYERS_END":
                    section = None
                    continue

                # Single layer
                elif line == "LAYER_START":
                    current_layer = {'effects': []}
                    continue
                elif line == "LAYER_END":
                    if current_item:
                        current_item['layers'].append(current_layer)
                    current_layer = None
                    continue

                # Effects section
                elif line == "EFFECTS_START":
                    section = "effects"
                    continue
                elif line == "EFFECTS_END":
                    section = None
                    continue

                # Footage section
                elif line == "FOOTAGE_START":
                    section = "footage"
                    continue
                elif line == "FOOTAGE_END":
                    section = None
                    continue

                # Footage item
                elif line == "FOOTAGE_ITEM_START":
                    current_item = {}
                    continue
                elif line == "FOOTAGE_ITEM_END":
                    result['footage'].append(current_item)
                    current_item = None
                    continue

                # Parse key-value pairs
                if "=" in line:
                    key, value = line.split("=", 1)

                    # Handle effects specially
                    if key == "effect":
                        matchName, name = value.split(",", 1)
                        if current_layer:
                            current_layer['effects'].append({
                                'matchName': matchName,
                                'name': name
                            })
                        continue

                    # Convert values to appropriate types
                    if value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False
                    else:
                        try:
                            value = float(value)
                            # Convert to int if it's a whole number
                            if value.is_integer():
                                value = int(value)
                        except ValueError:
                            pass

                    # Add to appropriate section
                    if section == "project_info":
                        result['project_info'][key] = value
                    elif current_layer is not None:
                        current_layer[key] = value
                    elif current_item is not None:
                        current_item[key] = value

            return result

        except Exception as e:
            print(f"Error parsing output file: {str(e)}")
            return None

    @classmethod
    def create_project(cls, data: Dict) -> AEProject:
        """
        Creates project object from parsed data

        Args:
            data: Dictionary containing parsed project data

        Returns:
            AEProject instance with all parsed information
        """
        project_info = data['project_info']

        project = AEProject(
            name=project_info.get('name', ''),
            path=project_info.get('path', ''),
            version=project_info.get('version', ''),
            frame_rate=project_info.get('frameRate', 0.0),
            width=project_info.get('width', 0),
            height=project_info.get('height', 0),
            duration=project_info.get('duration', 0.0),
            bits_per_channel=project_info.get('bitsPerChannel', 8),
            working_color_space=project_info.get('workingColorSpace', ''),
            expression_engine=project_info.get('expressionEngine', ''),
            compositions=[],
            footage=[],
            folders=[]
        )

        # Create compositions
        for comp_data in data['compositions']:
            composition = AEComposition(
                name=comp_data.get('name', ''),
                id=comp_data.get('id', ''),
                duration=comp_data.get('duration', 0.0),
                frame_rate=comp_data.get('frameRate', 0.0),
                width=comp_data.get('width', 0),
                height=comp_data.get('height', 0),
                pixel_aspect=comp_data.get('pixelAspect', 1.0),
                background_color=comp_data.get('bgColor', '#000000'),
                work_area_start=comp_data.get('workAreaStart', 0.0),
                work_area_duration=comp_data.get('workAreaDuration', 0.0),
                layers=[],
                markers=[]
            )

            # Add layers to composition
            for layer_data in comp_data.get('layers', []):
                layer = AELayer(
                    name=layer_data.get('name', ''),
                    index=layer_data.get('index', 0),
                    type=layer_data.get('type', ''),
                    enabled=layer_data.get('enabled', True),
                    solo=layer_data.get('solo', False),
                    shy=layer_data.get('shy', False),
                    in_point=layer_data.get('inPoint', 0.0),
                    out_point=layer_data.get('outPoint', 0.0),
                    start_time=layer_data.get('startTime', 0.0),
                    stretch=layer_data.get('stretch', 100.0),
                    quality=layer_data.get('quality', 'BEST'),
                    source_name=layer_data.get('sourceName'),
                    source_path=layer_data.get('sourcePath'),
                    parent=layer_data.get('parent'),
                    blending_mode=layer_data.get('blendingMode', 'normal'),
                    three_d_layer=layer_data.get('threeDLayer', False),
                    preserve_transparency=layer_data.get('preserveTransparency', False),
                    effects=layer_data.get('effects', []),
                    markers=[]
                )
                composition.add_layer(layer)

            project.add_composition(composition)

        # Create footage items
        for footage_data in data['footage']:
            footage = AEFootage(
                name=footage_data.get('name', ''),
                id=footage_data.get('id', ''),
                path=footage_data.get('path', ''),
                width=footage_data.get('width'),
                height=footage_data.get('height'),
                duration=footage_data.get('duration'),
                pixel_aspect=footage_data.get('pixelAspect', 1.0),
                has_video=footage_data.get('hasVideo', False),
                has_audio=footage_data.get('hasAudio', False),
                is_still=footage_data.get('isStill', False),
                native_fps=footage_data.get('nativeFps'),
                field_order=footage_data.get('fieldOrder'),
                alpha_mode=footage_data.get('alphaMode'),
                is_sequence=footage_data.get('isSequence', False),
                sequence_start=footage_data.get('sequenceStart'),
                sequence_duration=footage_data.get('sequenceDuration'),
                sequence_frame_rate=footage_data.get('sequenceFrameRate')
            )
            project.add_footage(footage)

        return project
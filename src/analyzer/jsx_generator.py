class JSXGenerator:
    """Class for generating JSX scripts for project analysis"""

    @staticmethod
    def create_analysis_script(project_path: str, output_path: str) -> str:
        """
        Generates JSX script for project analysis

        Args:
            project_path: Path to After Effects project file
            output_path: Path where analysis results will be saved

        Returns:
            Complete JSX script as string
        """
        return f'''
        // Set up logging
        var logFile = new File("{output_path}.log");
        logFile.open("w");

        function writeLog(msg) {{
            logFile.write(msg + "\\n");
            logFile.close();
            logFile.open("a");
        }}

        try {{
            // Open project file
            var proj = app.open(new File("{project_path}"));
            if (!proj) throw new Error("Could not open project file");

            // Set up output file
            var output = new File("{output_path}");
            output.open("w");

            // Project Info
            {JSXGenerator.get_project_info_script()}

            // Analyze compositions
            {JSXGenerator.get_composition_analysis_script()}

            // Analyze footage
            {JSXGenerator.get_footage_analysis_script()}

            // Clean up
            output.close();
            app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
            writeLog("Analysis completed successfully");

        }} catch(error) {{
            writeLog("Error: " + error.toString());
            if (output && output.exists) {{
                output.close();
            }}
            if (app.project) {{
                app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
            }}
        }}
        '''

    @staticmethod
    def get_project_info_script() -> str:
        """Returns script part responsible for project information"""
        return '''
            output.writeln("PROJECT_INFO_START");
            output.writeln("name=" + app.project.file.name);
            output.writeln("path=" + app.project.file.fsName);
            output.writeln("version=" + app.version);
            output.writeln("frameRate=" + app.project.frameRate);
            output.writeln("width=" + app.project.width);
            output.writeln("height=" + app.project.height);
            output.writeln("duration=" + app.project.duration);
            output.writeln("bitsPerChannel=" + app.project.bitsPerChannel);
            output.writeln("workingColorSpace=" + app.project.workingColorSpace);
            output.writeln("expressionEngine=" + app.project.expressionEngine);
            output.writeln("PROJECT_INFO_END");
        '''

    @staticmethod
    def get_composition_analysis_script() -> str:
        """Returns script part responsible for composition analysis"""
        return '''
            output.writeln("COMPOSITIONS_START");
            for (var i = 1; i <= app.project.numItems; i++) {
                var item = app.project.item(i);
                if (item instanceof CompItem) {
                    output.writeln("COMP_START");
                    output.writeln("name=" + item.name);
                    output.writeln("id=" + item.id);
                    output.writeln("duration=" + item.duration);
                    output.writeln("frameRate=" + item.frameRate);
                    output.writeln("width=" + item.width);
                    output.writeln("height=" + item.height);
                    output.writeln("pixelAspect=" + item.pixelAspect);
                    output.writeln("bgColor=" + item.bgColor);
                    output.writeln("workAreaStart=" + item.workAreaStart);
                    output.writeln("workAreaDuration=" + item.workAreaDuration);

                    // Analyze layers
                    output.writeln("LAYERS_START");
                    for (var j = 1; j <= item.numLayers; j++) {
                        var layer = item.layer(j);
                        output.writeln("LAYER_START");
                        output.writeln("name=" + layer.name);
                        output.writeln("index=" + layer.index);
                        output.writeln("type=" + layer.constructor.name);
                        output.writeln("enabled=" + layer.enabled);
                        output.writeln("solo=" + layer.solo);
                        output.writeln("shy=" + layer.shy);
                        output.writeln("inPoint=" + layer.inPoint);
                        output.writeln("outPoint=" + layer.outPoint);
                        output.writeln("startTime=" + layer.startTime);
                        output.writeln("stretch=" + layer.stretch);
                        output.writeln("quality=" + layer.quality);
                        output.writeln("threeDLayer=" + layer.threeDLayer);
                        output.writeln("blendingMode=" + layer.blendingMode);
                        output.writeln("preserveTransparency=" + layer.preserveTransparency);

                        if (layer.source) {
                            output.writeln("sourceName=" + layer.source.name);
                            if (layer.source.file) {
                                output.writeln("sourcePath=" + layer.source.file.fsName);
                            }
                        }

                        if (layer.parent) {
                            output.writeln("parent=" + layer.parent.name);
                        }

                        // Analyze effects
                        if (layer.property("ADBE Effect Parade")) {
                            var effects = layer.property("ADBE Effect Parade");
                            output.writeln("EFFECTS_START");
                            for (var k = 1; k <= effects.numProperties; k++) {
                                var effect = effects.property(k);
                                output.writeln("effect=" + effect.matchName + "," + effect.name);
                            }
                            output.writeln("EFFECTS_END");
                        }

                        output.writeln("LAYER_END");
                    }
                    output.writeln("LAYERS_END");

                    output.writeln("COMP_END");
                }
            }
            output.writeln("COMPOSITIONS_END");
        '''

    @staticmethod
    def get_footage_analysis_script() -> str:
        """Returns script part responsible for footage analysis"""
        return '''
            output.writeln("FOOTAGE_START");
            for (var i = 1; i <= app.project.numItems; i++) {
                var item = app.project.item(i);
                if (item instanceof FootageItem) {
                    output.writeln("FOOTAGE_ITEM_START");
                    output.writeln("name=" + item.name);
                    output.writeln("id=" + item.id);

                    if (item.file) {
                        output.writeln("path=" + item.file.fsName);
                    }

                    output.writeln("width=" + item.width);
                    output.writeln("height=" + item.height);
                    output.writeln("duration=" + item.duration);
                    output.writeln("pixelAspect=" + item.pixelAspect);
                    output.writeln("hasVideo=" + item.hasVideo);
                    output.writeln("hasAudio=" + item.hasAudio);
                    output.writeln("isStill=" + item.isStill);

                    if (item.mainSource) {
                        output.writeln("nativeFps=" + item.mainSource.nativeFps);
                        output.writeln("fieldOrder=" + item.mainSource.fieldOrder);
                        output.writeln("alphaMode=" + item.mainSource.alphaMode);

                        if (item.mainSource.isSequence) {
                            output.writeln("isSequence=true");
                            output.writeln("sequenceStart=" + item.mainSource.sequenceStart);
                            output.writeln("sequenceDuration=" + item.mainSource.sequenceDuration);
                            output.writeln("sequenceFrameRate=" + item.mainSource.sequenceFrameRate);
                        }
                    }

                    output.writeln("FOOTAGE_ITEM_END");
                }
            }
            output.writeln("FOOTAGE_END");
        '''
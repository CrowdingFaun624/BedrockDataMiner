from typing import IO
import json

import DataMiners.SoundDefinitions.SoundDefinitionsDataMiner as SoundDefinitionsDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class SoundDefinitionsDataMiner1(SoundDefinitionsDataMiner.SoundDefinitionsDataMiner):
    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]]:
        path = "sounds/sounds.json"
        if not self.file_exists(path):
            raise FileNotFoundError("No \"sound_definitions.json\" files found in \"%s\"" % self.version)
        sound_definitions_file:dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict] = json.loads(self.read_file(path, "t"))
        
        sound_definitions:dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]] = {}
        for sound_name, sound_properties in sound_definitions_file.items():
            sound_definitions[sound_name] = {"vanilla": sound_properties}

        return {key: value for key, value in sorted(sound_definitions.items())}

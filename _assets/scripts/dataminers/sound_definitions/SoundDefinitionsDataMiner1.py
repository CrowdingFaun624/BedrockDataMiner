import json

import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting

__all__ = ["SoundDefinitionsDataMiner1"]

class SoundDefinitionsDataMiner1(DataMiner.DataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]]:
        path = "sounds/sounds.json"
        accessor = self.get_accessor("client")
        if not accessor.file_exists(path):
            raise Exceptions.DataMinerNothingFoundError(self)
        sound_definitions_file:dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict] = json.loads(accessor.read(path, "t"))

        sound_definitions:dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]] = {}
        for sound_name, sound_properties in sound_definitions_file.items():
            sound_definitions[sound_name] = {"vanilla": sound_properties}

        return Sorting.sort_everything(sound_definitions)

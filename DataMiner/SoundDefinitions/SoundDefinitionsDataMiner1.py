import json

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.SoundDefinitions.SoundDefinitionsDataMiner as SoundDefinitionsDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting


class SoundDefinitionsDataMiner1(SoundDefinitionsDataMiner.SoundDefinitionsDataMiner):

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

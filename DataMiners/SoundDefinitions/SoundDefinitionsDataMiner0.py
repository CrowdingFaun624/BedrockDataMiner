from typing import IO
import pyjson5 # supports comments

import DataMiners.SoundDefinitions.SoundDefinitionsDataMiner as SoundDefinitionsDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class SoundDefinitionsDataMiner0(SoundDefinitionsDataMiner.SoundDefinitionsDataMiner):
    def normalize(self, file:IO) -> dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]:
        data = pyjson5.load(file)
        if "sound_definitions" in data:
            return data["sound_definitions"]
        else: return data

    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict|None=None) -> dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]]:
        resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = dependency_data["resource_packs"]
        resource_pack_names = [resource_pack["name"] for resource_pack in resource_packs]
        resource_pack_files = {"resource_packs/%s/sounds/sound_definitions.json" % resource_pack_name: resource_pack_name for resource_pack_name in resource_pack_names}
        files_request = [(resource_pack_file, "t", self.normalize) for resource_pack_file in resource_pack_files.keys()]
        files:dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]] = {key: value for key, value in self.read_files(files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise FileNotFoundError("No \"sound_definitions.json\" files found in \"%s\"" % self.version)
        
        sound_definitions:dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]] = {}
        for resource_pack_file, resource_pack_sound_definitions in files.items():
            resource_pack_name = resource_pack_files[resource_pack_file]
            for sound_name, sound_properties in resource_pack_sound_definitions.items():
                if sound_name not in sound_definitions:
                    sound_definitions[sound_name] = {resource_pack_name: sound_properties}
                else:
                    sound_definitions[sound_name][resource_pack_name] = sound_properties
        return sound_definitions

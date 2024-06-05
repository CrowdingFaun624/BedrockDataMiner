from typing import IO, Any, Callable, cast

import pyjson5  # supports comments

import DataMiners.DataMinerEnvironment as DataMinerEnvironment
import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.SoundDefinitions.SoundDefinitionsDataMiner as SoundDefinitionsDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting


class SoundDefinitionsDataMiner0(SoundDefinitionsDataMiner.SoundDefinitionsDataMiner):

    def normalize(self, file:IO[str]) -> dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]:
        data = cast(Callable[[IO[str]],Any], pyjson5.load)(file)
        if "sound_definitions" in data:
            return data["sound_definitions"]
        else: return data

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]]:
        resource_packs:DataMinerTyping.ResourcePacks = environment.dependency_data.get("resource_packs", self)
        resource_pack_names = [resource_pack["name"] for resource_pack in resource_packs]
        resource_pack_files = {"resource_packs/%s/sounds/sound_definitions.json" % resource_pack_name: resource_pack_name for resource_pack_name in resource_pack_names}
        files_request = [(resource_pack_file, "t", self.normalize) for resource_pack_file in resource_pack_files.keys()]
        accessor = self.get_accessor("client")
        files:dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]] = {key: value for key, value in self.read_files(accessor, files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        sound_definitions:dict[str,dict[str,DataMinerTyping.SoundDefinitionsJsonSoundEventTypedDict]] = {}
        for resource_pack_file, resource_pack_sound_definitions in files.items():
            resource_pack_name = resource_pack_files[resource_pack_file]
            for sound_name, sound_properties in resource_pack_sound_definitions.items():
                if sound_name not in sound_definitions:
                    sound_definitions[sound_name] = {resource_pack_name: sound_properties}
                else:
                    sound_definitions[sound_name][resource_pack_name] = sound_properties
        return Sorting.sort_everything(sound_definitions)

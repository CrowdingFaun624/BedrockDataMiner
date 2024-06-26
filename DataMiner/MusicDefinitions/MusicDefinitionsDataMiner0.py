import json

import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import DataMiner.MusicDefinitions.MusicDefinitionsDataMiner as MusicDefinitionsDataMiner
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting


class MusicDefinitionsDataMiner0(MusicDefinitionsDataMiner.MusicDefinitionsDataMiner):

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.MyMusicDefinitions:
        resource_packs:DataMinerTyping.ResourcePacks = environment.dependency_data.get("resource_packs", self)
        resource_pack_names = [resource_pack["name"] for resource_pack in resource_packs]
        resource_pack_files = {"resource_packs/%s/sounds/music_definitions.json" % resource_pack_name: resource_pack_name for resource_pack_name in resource_pack_names}
        files_request = [(resource_pack_file, "t", json.load) for resource_pack_file in resource_pack_files.keys()]
        accessor = self.get_accessor("client")
        files:dict[str,DataMinerTyping.MusicDefinitions] = {key: value for key, value in self.read_files(accessor, files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        music_definitions:DataMinerTyping.MyMusicDefinitions = {}
        for resource_pack_file, resource_pack_music_definitions in files.items():
            resource_pack_name = resource_pack_files[resource_pack_file]
            for environment_name, environment_properties in resource_pack_music_definitions.items():
                if environment_name not in music_definitions:
                    music_definitions[environment_name] = {resource_pack_name: environment_properties}
                else:
                    music_definitions[environment_name][resource_pack_name] = environment_properties
        return Sorting.sort_everything(music_definitions)

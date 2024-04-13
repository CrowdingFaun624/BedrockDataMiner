import json

import DataMiners.DataMinerTyping as DataMinerTyping
import DataMiners.MusicDefinitions.MusicDefinitionsDataMiner as MusicDefinitionsDataMiner
import Utilities.Sorting as Sorting

class MusicDefinitionsDataMiner0(MusicDefinitionsDataMiner.MusicDefinitionsDataMiner):

    def activate(self, dependency_data: DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.MyMusicDefinitions:
        resource_packs = dependency_data["resource_packs"]
        assert resource_packs is not None
        resource_pack_names = [resource_pack["name"] for resource_pack in resource_packs]
        resource_pack_files = {"resource_packs/%s/sounds/music_definitions.json" % resource_pack_name: resource_pack_name for resource_pack_name in resource_pack_names}
        files_request = [(resource_pack_file, "t", json.load) for resource_pack_file in resource_pack_files.keys()]
        files:dict[str,DataMinerTyping.MusicDefinitions] = {key: value for key, value in self.read_files(files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise FileNotFoundError("No \"music_definitions.json\" files found in \"%s\"" % self.version)

        music_definitions:DataMinerTyping.MyMusicDefinitions = {}
        for resource_pack_file, resource_pack_music_definitions in files.items():
            resource_pack_name = resource_pack_files[resource_pack_file]
            for environment_name, environment_properties in resource_pack_music_definitions.items():
                if environment_name not in music_definitions:
                    music_definitions[environment_name] = {resource_pack_name: environment_properties}
                else:
                    music_definitions[environment_name][resource_pack_name] = environment_properties
        return Sorting.sort_everything(music_definitions)

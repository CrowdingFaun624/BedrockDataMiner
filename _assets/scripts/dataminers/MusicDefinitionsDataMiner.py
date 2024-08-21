import _assets.scripts.dataminers.GrabPackFileDataMiner as GrabPackFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping

__all__ = ["MusicDefinitionsDataMiner"]

class MusicDefinitionsDataMiner(GrabPackFileDataMiner.GrabPackFileDataMiner):

    def initialize(self, locations: list[str]) -> None:
        return super().initialize(locations, "resource_packs")

    def get_output(self, files:dict[str,DataMinerTyping.MusicDefinitions], pack_files: dict[str, str], environment: DataMinerEnvironment.DataMinerEnvironment) -> DataMinerTyping.MyMusicDefinitions:
        output:DataMinerTyping.MyMusicDefinitions = {}
        for file_name, music_definitions in files.items():
            pack_name = pack_files[file_name]
            for environment_name, environment_properties in music_definitions.items():
                if environment_name not in output:
                    output[environment_name] = {pack_name: environment_properties}
                else:
                    output[environment_name][pack_name] = environment_properties
        return output

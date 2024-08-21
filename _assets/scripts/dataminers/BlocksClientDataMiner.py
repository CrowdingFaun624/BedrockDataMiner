import _assets.scripts.dataminers.GrabPackFileDataMiner as GrabPackFileDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import _assets.scripts.dataminers.DataMinerTyping as DataMinerTyping
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

__all__ = ["BlocksClientDataMiner"]

class BlocksClientDataMiner(GrabPackFileDataMiner.GrabPackFileDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))
    )

    def initialize(self, locations:list[str]) -> None:
        super().initialize(locations, "resource_packs")

    def get_output(self, files: dict[str,dict[str,DataMinerTyping.BlocksJsonClientBlockTypedDict]], pack_files: dict[str, str], environment: DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.MyBlocksJsonClientBlockTypedDict]:
        output:dict[str,DataMinerTyping.MyBlocksJsonClientBlockTypedDict] = {} # temporarily in dict so it can be easily created.
        for file_name, blocks in files.items():
            pack_name = pack_files[file_name]
            for block_name, block_properties in blocks.items():
                if block_name == "format_version": continue
                if block_name not in output:
                    output[block_name] = {"name": block_name, "properties": {pack_name: block_properties}}
                else:
                    output[block_name]["properties"][pack_name] = block_properties
        return sorted((value for value in output.values()), key=lambda x: x["name"])

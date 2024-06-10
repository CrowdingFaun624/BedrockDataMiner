from typing import IO, Any, Callable, cast

import pyjson5  # supports comments

import DataMiner.BlocksClient.BlocksClientDataMiner as BlocksDataMiner
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.DataMinerTyping as DataMinerTyping
import Utilities.Exceptions as Exceptions
import Utilities.Sorting as Sorting
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class BlocksClientDataMiner0(BlocksDataMiner.BlocksClientDataMiner):

    parameters = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("blocks_locations", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))
    )

    def initialize(self, **kwargs) -> None:
        self.blocks_locations:list[str] = kwargs["blocks_locations"]

    def activate(self, environment:DataMinerEnvironment.DataMinerEnvironment) -> list[DataMinerTyping.MyBlocksJsonClientBlockTypedDict]:
        resource_packs:DataMinerTyping.ResourcePacks = environment.dependency_data.get("resource_packs", self)
        resource_pack_names = [(resource_pack["name"], resource_pack["path"]) for resource_pack in resource_packs]
        resource_pack_files:dict[str,str] = {}
        for blocks_location in self.blocks_locations:
            resource_pack_files.update({resource_pack_path + blocks_location: resource_pack_name for resource_pack_name, resource_pack_path in resource_pack_names})
        files_request = [(resource_pack_file, "t", cast(Callable[[IO[str]],Any], pyjson5.load)) for resource_pack_file in resource_pack_files.keys()]
        accessor = self.get_accessor("client")
        files:dict[str,dict[str,DataMinerTyping.BlocksJsonClientBlockTypedDict]] = {key: value for key, value in self.read_files(accessor, files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise Exceptions.DataMinerNothingFoundError(self)

        blocks:dict[str,DataMinerTyping.MyBlocksJsonClientBlockTypedDict] = {} # temporarily in dict so it can be easily created.
        for resource_pack_file, resource_pack_blocks in files.items():
            resource_pack_name = resource_pack_files[resource_pack_file]
            for block_name, block_properties in resource_pack_blocks.items():
                if block_name == "format_version": continue
                if block_name not in blocks:
                    blocks[block_name] = {"name": block_name, "properties": {resource_pack_name: block_properties}}
                else:
                    blocks[block_name]["properties"][resource_pack_name] = block_properties
        return sorted((Sorting.sort_everything(value) for value in blocks.values()), key=lambda x: x["name"])

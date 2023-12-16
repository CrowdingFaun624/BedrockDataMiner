import pyjson5 # supports comments
from typing import Any

import DataMiners.Blocks.BlocksDataMiner as BlocksDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class BlocksDataMiner0(BlocksDataMiner.BlocksDataMiner):
    def activate(self, dependency_data:dict[str,Any]|None=None) -> dict[str,dict[str,DataMinerTyping.BlocksJsonBlockTypedDict]]:
        resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = dependency_data["resource_packs"]
        resource_pack_names = [resource_pack["name"] for resource_pack in resource_packs]
        resource_pack_files = {"resource_packs/%s/blocks.json" % resource_pack_name: resource_pack_name for resource_pack_name in resource_pack_names}
        files_request = [(resource_pack_file, "t", pyjson5.load) for resource_pack_file in resource_pack_files.keys()]
        files:dict[str,dict[str,Any]] = {key: value for key, value in self.read_files(files_request, non_exist_ok=True).items() if value is not None}
        if len(files) == 0:
            raise FileNotFoundError("No \"blocks.json\" files found in \"%s\"" % self.version)
        
        blocks:dict[str,dict[str,DataMinerTyping.BlocksJsonBlockTypedDict]] = {} # temporarily in dict so it can be easily created.
        for resource_pack_file, resource_pack_blocks in files.items():
            resource_pack_name = resource_pack_files[resource_pack_file]
            for block_name, block_properties in resource_pack_blocks.items():
                if block_name == "format_version": continue
                if block_name not in blocks:
                    blocks[block_name] = {resource_pack_name: block_properties}
                else:
                    blocks[block_name][resource_pack_name] = block_properties
        return list(blocks.values())

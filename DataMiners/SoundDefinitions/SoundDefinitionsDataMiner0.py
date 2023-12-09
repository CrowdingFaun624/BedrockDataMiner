from typing import Any
import pyjson5 # supports comments

import DataMiners.SoundDefinitions.SoundDefinitionsDataMiner as SoundDefinitionsDataMiner
import DataMiners.DataMinerTyping as DataMinerTyping

class SoundDefinitionsDataMiner0(SoundDefinitionsDataMiner.SoundDefinitionsDataMiner):
    def activate(self, dependency_data: dict[str, Any] | None = None) -> Any:
        resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = dependency_data["resource_packs"]
        resource_pack_names = [resource_pack["name"] for resource_pack in resource_packs]
        resource_pack_files = {"resource_packs/%s/blocks.json" % resource_pack_name: resource_pack_name for resource_pack_name in resource_pack_names}
        files_request = [(resource_pack_file, "t", pyjson5.load) for resource_pack_file in resource_pack_files.keys()]

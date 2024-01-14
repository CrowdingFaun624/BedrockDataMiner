'''Returns a list of resource packs that the version has, its type, and an ID that can be used to correctly sort the packs.
[
    {
        "name": "vanilla",
        "type": ["core"|"education"|"experimental"|"extra"|"vanity", ...],
        "id": 0
    },
    ...
]'''

import DataMiners.DataMiner as DataMiner
import DataMiners.ResourcePacks.ResourcePacksDataMiner0 as ResourcePacksDataMiner0

dataminers = DataMiner.DataMinerCollection("resource_packs.json", "resource_packs", [
    DataMiner.DataMinerSettings("a0.17.0.2", "-", ResourcePacksDataMiner0.ResourcePacksDataMiner0, resource_packs_folder="resource_packs"),
    DataMiner.DataMinerSettings("a0.15.0_build1", "a0.17.0.2", ResourcePacksDataMiner0.ResourcePacksDataMiner0, resource_packs_folder="resourcepacks"),
    # Prior to a0.15.0_build1, resource packs did not exist.
])
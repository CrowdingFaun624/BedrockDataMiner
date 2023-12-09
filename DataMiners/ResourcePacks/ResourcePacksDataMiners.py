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
    DataMiner.DataMinerSettings("-", "-", ResourcePacksDataMiner0.ResourcePacksDataMiner0)
])
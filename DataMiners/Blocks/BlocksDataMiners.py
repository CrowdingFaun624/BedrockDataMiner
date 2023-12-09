'''Returns a list of blocks.
[
    {
        "name": "minecraft:stone",
        "defined_in": ["vanilla", "experimental_update_announced_live2023"],
        "properties": {
            "isotropic": true,
            "textures": "dirt",
            "sound": "gravel"
        }
    }
]'''

import DataMiners.DataMiner as DataMiner
import DataMiners.Blocks.BlocksDataMiner0 as BlocksDataMiner0

dataminers = DataMiner.DataMinerCollection("blocks.json", "blocks", [
    DataMiner.DataMinerSettings("-", "-", BlocksDataMiner0.BlocksDataMiner0, ["resource_packs"])
])
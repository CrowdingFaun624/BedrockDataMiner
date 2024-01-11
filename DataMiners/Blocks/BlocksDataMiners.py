'''Returns a list of blocks.
[
    {
        "name": "minecraft:stone",
        "properties": {
            "vanilla": {
                "isotropic": true,
                "textures": "dirt",
                "sound": "gravel"
            },
            "experimental_update_announced_live2023": {
                "sound": "stone"
            }
        }
    }
]'''

import DataMiners.DataMiner as DataMiner
import DataMiners.Blocks.BlocksDataMiner0 as BlocksDataMiner0

dataminers = DataMiner.DataMinerCollection("blocks.json", "blocks", [
    DataMiner.DataMinerSettings("-", "-", BlocksDataMiner0.BlocksDataMiner0, ["resource_packs"])
])
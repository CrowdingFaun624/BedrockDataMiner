import DataMiners.DataMiner as DataMiner
import DataMiners.Blocks.BlocksDataMiner0 as BlocksDataMiner0

dataminers = DataMiner.DataMinerCollection("blocks.json", "blocks", [
    DataMiner.DataMinerSettings("-", "-", BlocksDataMiner0.BlocksDataMiner0)
])
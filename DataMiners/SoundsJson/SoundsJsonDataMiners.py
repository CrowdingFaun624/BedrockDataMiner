
import DataMiners.DataMiner as DataMiner
import DataMiners.SoundsJson.SoundsJsonDataMiner0 as SoundsJsonDataMiner0

dataminers = DataMiner.DataMinerCollection("sounds.json", "sounds_json", [
    DataMiner.DataMinerSettings("-", "-", SoundsJsonDataMiner0.SoundsJsonDataMiner0, ["resource_packs"])
])
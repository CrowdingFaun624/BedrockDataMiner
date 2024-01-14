
import DataMiners.DataMiner as DataMiner
import DataMiners.SoundsJson.SoundsJsonDataMiner0 as SoundsJsonDataMiner0

dataminers = DataMiner.DataMinerCollection("sounds.json", "sounds_json", [
    DataMiner.DataMinerSettings("a0.17.0.2", "-", SoundsJsonDataMiner0.SoundsJsonDataMiner0, ["resource_packs"], sounds_json_locations=["resource_packs/%s/sounds.json"]),
    DataMiner.DataMinerSettings("a0.16.0_build4", "a0.17.0.2", SoundsJsonDataMiner0.SoundsJsonDataMiner0, ["resource_packs"], sounds_json_locations=["resourcepacks/%s/sounds.json", "resourcepacks/%s/client/sounds.json"]),
    # Prior to a0.16.0_build4, there is no sounds.json file. The data is stored in the code and cannot be easily accessed.
])
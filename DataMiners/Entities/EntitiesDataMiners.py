
import DataMiners.DataMiner as DataMiner
import DataMiners.Entities.EntitiesComparer as EntitiesComparer
import DataMiners.Entities.EntitiesDataMiner0 as EntitiesDataMiner0

dataminers = DataMiner.DataMinerCollection("entities.json", "entities", EntitiesComparer.comparer, [
    DataMiner.DataMinerSettings("-", "-", EntitiesDataMiner0.EntitiesDataMiner0, ["behavior_packs"], behavior_packs_location="behavior_packs"),
])

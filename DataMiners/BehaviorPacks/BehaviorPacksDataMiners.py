import DataMiners.BehaviorPacks.BehaviorPacksComparer as BehaviorPacksComparer
import DataMiners.BehaviorPacks.BehaviorPacksDataMiner0 as BehaviorPacksDataMiner0
import DataMiners.DataMiner as DataMiner

dataminers = DataMiner.DataMinerCollection("behavior_packs.json", "behavior_packs", BehaviorPacksComparer.comparer, [
    DataMiner.DataMinerSettings("-", "-", BehaviorPacksDataMiner0.BehaviorPacksDataMiner0, behavior_packs_folder="behavior_packs"),
])

import DataMiners.DataMiner as DataMiner
import DataMiners.Items.ItemsComparer as ItemsComparer
import DataMiners.Items.ItemsDataMiner0 as ItemsDataMiner0

dataminers = DataMiner.DataMinerCollection("items.json", "items", ItemsComparer.comparer, [
    DataMiner.DataMinerSettings("-", "-", ItemsDataMiner0.ItemsDataMiner0, ["behavior_packs"], behavior_packs_location="behavior_packs"),
])

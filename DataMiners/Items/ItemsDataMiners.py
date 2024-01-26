
import DataMiners.DataMiner as DataMiner
# import DataMiners.Items.ItemsComparer as ItemsComparer
import Comparison.Comparer as Comparer
import DataMiners.Items.ItemsDataMiner0 as ItemsDataMiner0

dataminers = DataMiner.DataMinerCollection("items.json", "items", Comparer.default_comparer, [
    DataMiner.DataMinerSettings("-", "-", ItemsDataMiner0.ItemsDataMiner0, ["behavior_packs"], behavior_packs_location="behavior_packs"),
])

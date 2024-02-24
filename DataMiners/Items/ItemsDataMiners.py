import DataMiners.Items.ItemsDataMiner0 as ItemsDataMiner0

# dataminers = DataMiner.DataMinerCollection("items.json", "items", ItemsComparer.comparer, [
#     DataMiner.DataMinerSettings("-", "-", ItemsDataMiner0.ItemsDataMiner0, ["behavior_packs"], behavior_packs_location="behavior_packs"),
# ])

dataminers = [
    ItemsDataMiner0.ItemsDataMiner0,
]

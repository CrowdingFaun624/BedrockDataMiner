import DataMiners.LootTables.LootTablesDataMiner0 as LootTablesDataMiner0

# dataminers = DataMiner.DataMinerCollection("loot_tables.json", "loot_tables", LootTablesComparer.comparer, [
#     DataMiner.DataMinerSettings("-", "-", LootTablesDataMiner0.LootTablesDataMiner0, ["behavior_packs"], behavior_packs_location="behavior_packs"),
# ])

dataminers = [
    LootTablesDataMiner0.LootTablesDataMiner0,
]

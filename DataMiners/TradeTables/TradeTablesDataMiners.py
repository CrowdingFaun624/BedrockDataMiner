import DataMiners.TradeTables.TradeTablesDataMiner0 as TradeTablesDataMiner0

# dataminers = DataMiner.DataMinerCollection("trade_tables.json", "trade_tables", Comparer.default_comparer, [
#     DataMiner.DataMinerSettings("-", "-", TradeTablesDataMiner0.TradeTablesDataMiner0, ["behavior_packs"], behavior_packs_location="behavior_packs"),
# ])

dataminers = [
    TradeTablesDataMiner0.TradeTablesDataMiner0,
]

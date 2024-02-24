import DataMiners.Credits.CreditsDataMiner0 as CreditsDataMiner0

# dataminers = DataMiner.DataMinerCollection("credits.json", "credits", CreditsComparer.comparer, [
#     DataMiner.DataMinerSettings("-", "-", CreditsDataMiner0.CreditsDataMiner0, [])
# ])

dataminers = [
    CreditsDataMiner0.CreditsDataMiner0,
]

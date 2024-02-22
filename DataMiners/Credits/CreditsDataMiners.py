import DataMiners.Credits.CreditsComparer as CreditsComparer
import DataMiners.Credits.CreditsDataMiner0 as CreditsDataMiner0
import DataMiners.DataMiner as DataMiner

dataminers = DataMiner.DataMinerCollection("credits.json", "credits", CreditsComparer.comparer, [
    DataMiner.DataMinerSettings("-", "-", CreditsDataMiner0.CreditsDataMiner0, [])
])

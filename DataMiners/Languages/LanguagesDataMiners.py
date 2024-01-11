import DataMiners.DataMiner as DataMiner
import DataMiners.Languages.LanguagesDataMiner0 as LanguagesDataMiner0

dataminers = DataMiner.DataMinerCollection("languages.json", "languages", [
    DataMiner.DataMinerSettings("-", "-", LanguagesDataMiner0.LanguagesDataMiner0, ["resource_packs"])
])
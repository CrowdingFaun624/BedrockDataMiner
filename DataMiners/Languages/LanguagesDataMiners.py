import DataMiners.DataMiner as DataMiner
import DataMiners.Languages.LanguagesDataMiner0 as LanguagesDataMiner0
import DataMiners.Languages.LanguagesDataMiner1 as LanguagesDataMiner1
import DataMiners.Languages.LanguagesDataMiner2 as LanguagesDataMiner2
import DataMiners.Languages.LanguagesDataMiner3 as LanguagesDataMiner3

dataminers = DataMiner.DataMinerCollection("languages.json", "languages", [
    DataMiner.DataMinerSettings("1.1.0", "-", LanguagesDataMiner0.LanguagesDataMiner0, ["resource_packs"]),
    DataMiner.DataMinerSettings("a0.17.0.2", "1.1.0", LanguagesDataMiner1.LanguagesDataMiner1, ["resource_packs"], languages_location="resource_packs/%s/texts/languages.json"),
    DataMiner.DataMinerSettings("a0.16.0_build4", "a0.17.0.2", LanguagesDataMiner1.LanguagesDataMiner1, ["resource_packs"], languages_location="resourcepacks/%s/texts/languages.json"),
    DataMiner.DataMinerSettings("a0.14.0_build1", "a0.16.0_build4", LanguagesDataMiner2.LanguagesDataMiner2, [], languages_location="loc/languages.json"),
    DataMiner.DataMinerSettings("a0.13.2-2", "a0.14.0_build1", LanguagesDataMiner2.LanguagesDataMiner2, [], languages_location="lang/languages.json"),
    DataMiner.DataMinerSettings("a0.11.0_build1", "a0.13.2-1", LanguagesDataMiner2.LanguagesDataMiner2, [], languages_location="lang/languages.json"), # weird gap because a0.13.2-1 does not have language files for some reason
    DataMiner.DataMinerSettings("a0.3.0-1", "a0.11.0_build1", LanguagesDataMiner3.LanguagesDataMiner3, []),
])

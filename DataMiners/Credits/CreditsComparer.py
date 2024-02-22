import Comparison.ComparerImporter as ComparerImporter
import DataMiners.DataMinerTyping as DataMinerTyping

def convert(data:DataMinerTyping.Credits, dependencies:DataMinerTyping.DependenciesTypedDict) -> dict:
    return {section["section"]: {discipline["discipline"]: {title["title"]: title["names"] for title in discipline["titles"]} for discipline in section["disciplines"]} for section in data}

comparer = ComparerImporter.load_from_file("credits", {
    "convert": convert,
})

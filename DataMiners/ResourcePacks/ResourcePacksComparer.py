import DataMiners.DataMinerTyping as DataMinerTyping
import Comparison.ComparerImporter as ComparerImporter

def normalize(data:DataMinerTyping.ResourcePacks, dependencies:DataMinerTyping.DependenciesTypedDict) -> list[str]:
    return [resource_pack["name"] for resource_pack in data]

comparer = ComparerImporter.load_from_file("resource_packs", {"normalize": normalize})

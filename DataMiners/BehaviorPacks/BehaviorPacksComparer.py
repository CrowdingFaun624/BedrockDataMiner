import DataMiners.DataMinerTyping as DataMinerTyping
import Comparison.ComparerImporter as ComparerImporter

def normalize(data:DataMinerTyping.BehaviorPacks, dependencies:DataMinerTyping.DependenciesTypedDict) -> list[str]:
    return [behavior_pack["name"] for behavior_pack in data]

comparer = ComparerImporter.load_from_file("behavior_packs", {"normalize": normalize})

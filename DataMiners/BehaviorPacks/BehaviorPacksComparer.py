from typing import TYPE_CHECKING

import DataMiners.DataMinerTyping as DataMinerTyping
import Comparison.ComparerImporter as ComparerImporter

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.BehaviorPacks, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> list[str]:
    return [behavior_pack["name"] for behavior_pack in data]

comparer = ComparerImporter.load_from_file("behavior_packs", {"normalize": normalize})

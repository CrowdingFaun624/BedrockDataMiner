from typing import TYPE_CHECKING

import DataMiners.DataMinerTyping as DataMinerTyping
import Comparison.ComparerImporter as ComparerImporter

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.ResourcePacks, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> list[str]:
    return [resource_pack["name"] for resource_pack in data]

comparer = ComparerImporter.load_from_file("resource_packs", {"normalize": normalize, "post_normalize": lambda data: sorted(data)})

from typing import TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.ResourcePacks, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> list[str]:
    return [resource_pack["name"] for resource_pack in data]

comparer = Comparer.Comparer(
    normalizer=normalize,
    post_normalizer=lambda data: sorted(data),
    dependencies=None,
    base_comparer_section=Comparer.ListComparerSection(
        name="resource pack",
        types=(str,),
        comparer=None,
        measure_length=True,
        ordered=False
    )
)
from typing import TYPE_CHECKING

import Comparison.Compare as Compare
import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.DuplicateSounds, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.NormalizedDuplicateSounds:
    return {sha1_hash: Compare.UnorderedList(duplicate_sounds) for sha1_hash, duplicate_sounds in data.items()}

comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=None,
    base_comparer_section=Comparer.DictComparerSection(
        name="duplicate sound",
        key_types=(str,),
        value_types=(list,),
        comparer=Comparer.ListComparerSection(
            name="sound",
            types=(dict,),
            ordered=False,
            comparer=Comparer.DictComparerSection(
                name="property",
                key_types=lambda key, value: key in ("file_name", "file_internal_name"),
                value_types=(str,),
                comparer=None
            )
        )
    )
)

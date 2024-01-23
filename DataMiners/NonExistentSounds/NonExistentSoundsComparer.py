from typing import TYPE_CHECKING

import Comparison.Compare as Compare
import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.NonExistentSounds, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.NormalizedNonExistentSounds:
    resource_packs = dataminers["resource_packs"].get_data_file(version, non_exist_ok=True)
    if resource_packs is None: resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]
    return {sound_event_name: CollapseResourcePacks.collapse_resource_packs({resource_pack_name: Compare.UnorderedList(resource_pack_properties) for resource_pack_name, resource_pack_properties in sound_event_properties.items()}, resource_packs, version.name, False) for sound_event_name, sound_event_properties in data.items()}

comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=["resource_packs"],
    base_comparer_section=Comparer.DictComparerSection(
        name="sound event",
        key_types=(str,),
        value_types=(dict,),
        detect_key_moves=True,
        comparer=Comparer.DictComparerSection(
            name="resource pack",
            key_types=(str,),
            value_types=(Compare.UnorderedList,),
            detect_key_moves=True,
            comparer=Comparer.ListComparerSection(
                name="sound location",
                types=(str,),
                comparer=None,
                ordered=False
            )
        )
    )
)

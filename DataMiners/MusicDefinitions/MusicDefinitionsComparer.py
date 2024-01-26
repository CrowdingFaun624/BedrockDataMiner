from typing import TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.MyMusicDefinitions, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.MyMusicDefinitions:
    resource_packs:DataMinerTyping.ResourcePacks = dataminers["resource_packs"].get_data_file(version, non_exist_ok=True)
    if resource_packs is None:
        resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]
    return {environment_name: CollapseResourcePacks.collapse_resource_packs(environment_properties, resource_packs, version.name) for environment_name, environment_properties in data.items()}

comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=["resource_packs"],
    base_comparer_section=Comparer.DictComparerSection(
        name="environment",
        key_types=(str,),
        value_types=(dict,),
        measure_length=True,
        detect_key_moves=True,
        comparer=Comparer.DictComparerSection(
            name="resource pack",
            key_types=(str,),
            value_types=(dict,),
            measure_length=True,
            detect_key_moves=True,
            comparer=Comparer.TypedDictComparerSection(
                name="property",
                types=[
                    ("event_name", str, None),
                    ("min_delay", int, None),
                    ("max_delay", int, None),
                    ("defined_in", list, Comparer.ListComparerSection(
                        name="resource pack",
                        types=(str,),
                        print_flat=True,
                        comparer=None,
                    ))
                ]
            )
        )
    )
)

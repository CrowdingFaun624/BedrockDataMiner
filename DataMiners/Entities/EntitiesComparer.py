from typing import Any, TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

import DataMiners.Entities.EntitiesComparerComponents as EntitiesComparerComponents
import DataMiners.Entities.EntitiesComparerTemplates as EntitiesComparerTemplates

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.Entities, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.Entities:
    behavior_packs:DataMinerTyping.BehaviorPacks = dataminers["behavior_packs"].get_data_file(version, non_exist_ok=True)
    if behavior_packs is None:
        behavior_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]
    def fix_weird_components(entity_behavior_packs:dict[str,Any]) -> dict[str,Any]:
        # deletes components that are, for some reason, outside of the "components" or "component_groups" keys
        for behavior_pack_name, entity_data in entity_behavior_packs.items():
            for key_to_delete in [key for key in entity_data["minecraft:entity"] if key.startswith("minecraft:")]:
                del entity_data["minecraft:entity"][key_to_delete]
        return entity_behavior_packs
    return {entity_name: fix_weird_components(CollapseResourcePacks.collapse_resource_packs(entity_behavior_packs, behavior_packs, version.name)) for entity_name, entity_behavior_packs in data.items()}

def behavior_pack_comparison_move_function(key:str, value:DataMinerTyping.NormalizedBlocksJsonBlockTypedDict) -> DataMinerTyping.NormalizedBlocksJsonBlockTypedDict:
    output = value.copy()
    del output["defined_in"]
    return output

comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=["behavior_packs"],
    base_comparer_section=Comparer.DictComparerSection(
        name="entity",
        key_types=(str,),
        value_types=(dict,),
        detect_key_moves=False, # haha lol no not doing that right now
        measure_length=True,
        comparer=Comparer.DictComparerSection(
            name="behavior pack",
            key_types=(str,),
            value_types=(dict,),
            measure_length=True,
            detect_key_moves=True,
            comparison_move_function=behavior_pack_comparison_move_function,
            comparer=Comparer.UnnamedDictComparerSection(
                ("defined_in", list, Comparer.ListComparerSection(
                    name="behavior pack",
                    types=(str,),
                    ordered=False,
                    measure_length=True,
                    comparer=None,
                )),
                ("format_version", str, None),
                ("minecraft:entity", dict, Comparer.UnnamedDictComparerSection(
                    ("description", dict, Comparer.UnnamedDictComparerSection(
                        ("identifier", str, None),
                        ("is_spawnable", bool, None),
                        ("is_summonable", bool, None),
                        ("is_experimental", bool, None),
                        name="description"
                    )),
                    ("component_groups", dict, Comparer.DictComparerSection(
                        name="component group",
                        key_types=(str,),
                        value_types=(dict,),
                        measure_length=True,
                        comparer=EntitiesComparerComponents.comparer
                    )),
                    ("components", dict, EntitiesComparerComponents.comparer),
                    ("events", dict, EntitiesComparerTemplates.events_comparer),
                ))
            )
        )
    )
)
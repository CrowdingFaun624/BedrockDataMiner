from typing import TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.Languages, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.NormalizedLanguages:
    def fix_properties(unfixed_data:DataMinerTyping.LanguagesTypedDict, resource_packs:DataMinerTyping.ResourcePacks) -> dict[str,DataMinerTyping.LanguagesPropertiesTypedDict]:
        output = unfixed_data["properties"]
        for resource_pack in unfixed_data["defined_in"]:
            if resource_pack not in output:
                output[resource_pack] = {}
        return CollapseResourcePacks.collapse_resource_packs(output, resource_packs, version.name)

    resource_packs:DataMinerTyping.ResourcePacks = dataminers["resource_packs"].get_data_file(version, non_exist_ok=True)
    if resource_packs is None:
        resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]

    return {language["code"]: fix_properties(language, resource_packs) for language in data}

def languages_comparison_move_function(key:str, value:DataMinerTyping.LanguagesTypedDict) -> dict[str,str]|None:
    output = {resource_pack_name: resource_pack_properties["name"] for resource_pack_name, resource_pack_properties in value.items() if "name" in resource_pack_properties}
    return None if len(output) == 0 else output

comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=["resource_packs"],
    base_comparer_section=Comparer.DictComparerSection(
        name="language",
        key_types=(str,),
        value_types=(dict,),
        detect_key_moves=True,
        comparison_move_function=languages_comparison_move_function,
        measure_length=True,
        comparer=Comparer.DictComparerSection(
            name="resource pack",
            key_types=(str,),
            value_types=(dict,),
            comparer=Comparer.TypedDictComparerSection(
                name="property",
                types=[
                    ("name", str, None),
                    ("defined_in", list, Comparer.ListComparerSection(
                        name="resource pack",
                        types=(str,),
                        print_flat=True,
                        ordered=False,
                        comparer=None,
                    ))
                ]
            )
        )
    )
)

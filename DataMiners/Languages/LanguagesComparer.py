from typing import TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.Languages, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.NormalizedLanguages:
    def fix_properties(unfixed_data:DataMinerTyping.LanguagesTypedDict) -> dict[str,DataMinerTyping.LanguagesPropertiesTypedDict]:
        output = unfixed_data["properties"]
        for resource_pack in unfixed_data["defined_in"]:
            if resource_pack not in output:
                output[resource_pack] = {}
        return output
    return {language["code"]: fix_properties(language) for language in data}

def languages_comparison_move_function(key:str, value:DataMinerTyping.LanguagesTypedDict) -> dict[str,str]|None:
    output = {resource_pack_name: resource_pack_properties["name"] for resource_pack_name, resource_pack_properties in value.items() if "name" in resource_pack_properties}
    return None if len(output) == 0 else output

comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=None,
    base_comparer_section=Comparer.DictComparerSection(
        name="language",
        key_types=(str,),
        value_types=(dict,),
        detect_key_moves=True,
        comparison_move_function=languages_comparison_move_function,
        comparer=Comparer.DictComparerSection(
            name="resource pack",
            key_types=(str,),
            value_types=(dict,),
            comparer=Comparer.DictComparerSection(
                name="property",
                key_types=lambda key, value: key in "name",
                value_types=lambda key, value: isinstance(value, {
                    "name": (str,)
                }[key]),
                comparer=None
            )
        )
    )
)

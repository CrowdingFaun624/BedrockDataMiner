import Comparison.ComparerImporter as ComparerImporter
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks

def normalize(data:DataMinerTyping.Languages, dependencies:DataMinerTyping.DependenciesTypedDict) -> DataMinerTyping.NormalizedLanguages:

    def fix_properties(unfixed_data:DataMinerTyping.LanguagesTypedDict, resource_packs:DataMinerTyping.ResourcePacks) -> dict[str,DataMinerTyping.LanguagesPropertiesTypedDict]:
        output = unfixed_data["properties"]
        for resource_pack in unfixed_data["defined_in"]:
            if resource_pack not in output:
                output[resource_pack] = {}
        return CollapseResourcePacks.collapse_resource_packs(output, resource_packs)

    resource_packs:DataMinerTyping.ResourcePacks = dependencies["resource_packs"]
    if resource_packs is None:
        resource_packs = [{"name": "vanilla", "tags": ["core"], "id": 1}]

    a = {language["code"]: fix_properties(language, resource_packs) for language in data}
    return a

def languages_comparison_move_function(key:str, value:DataMinerTyping.LanguagesTypedDict) -> dict[str,str]|None:
    output = {resource_pack_name: resource_pack_properties["name"] for resource_pack_name, resource_pack_properties in value.items() if "name" in resource_pack_properties}
    return None if len(output) == 0 else output

comparer = ComparerImporter.load_from_file("languages", {
    "normalize": normalize,
    "languages_comparison_move_function": languages_comparison_move_function
})

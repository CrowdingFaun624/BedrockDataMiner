from typing import TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.CollapseResourcePacks as CollapseResourcePacks
# import Comparison.ComparerImporter as ComparerImporter

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.MyBlocks, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.NormalizedBlocks:
    def fix_properties(properties:DataMinerTyping.MyBlocksJsonBlockTypedDict) -> DataMinerTyping.MyBlocksJsonBlockTypedDict:
        for resource_pack_name, resource_pack_properties in properties.items():
            if "sounds" in resource_pack_properties: del resource_pack_properties["sounds"] # MCPE-76182
        return properties
    resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = dataminers["resource_packs"].get_data_file(version, True)
    output = {datum["name"]: CollapseResourcePacks.collapse_resource_packs(fix_properties(datum["properties"]), resource_packs, version.name) for datum in data}
    return output

def resource_pack_comparison_move_function(key:str, value:DataMinerTyping.NormalizedBlocksJsonBlockTypedDict) -> DataMinerTyping.NormalizedBlocksJsonBlockTypedDict:
    output = value.copy()
    del output["defined_in"]
    return output

# comparer = ComparerImporter.load_from_file("blocks", {"normalize": normalize, "resource_pack_comparison_move_function": resource_pack_comparison_move_function})
comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=["resource_packs"],
    base_comparer_section=Comparer.DictComparerSection(
        name="block",
        key_types=(str,),
        value_types=(dict,),
        detect_key_moves=True,
        measure_length=True,
        comparer=Comparer.DictComparerSection(
            name="resource pack",
            key_types=(str,),
            value_types=(dict,),
            detect_key_moves=True,
            comparison_move_function=resource_pack_comparison_move_function,
            measure_length=True,
            comparer=Comparer.TypedDictComparerSection(
                name="property",
                types=[
                    ("blockshape", str, None),
                    ("brightness_gamma", float, None),
                    ("carried_textures", (str, dict), [
                        (lambda key, value: isinstance(value, str), None),
                        (lambda key, value: isinstance(value, dict), Comparer.DictComparerSection(
                            name="direction",
                            comparer=None,
                            key_types=lambda key, value: key in ("down", "east", "north", "side", "south", "up", "west"),
                            value_types=(str,)
                        ))
                    ]),
                    ("defined_in", list, Comparer.ListComparerSection(
                        name="resource pack",
                        comparer=None,
                        types=(str,),
                        print_flat=True,
                        ordered=False
                    )),
                    ("isotropic", (bool, dict), [
                        (lambda key, value: isinstance(value, bool), None),
                        (lambda key, value: isinstance(value, dict), Comparer.DictComparerSection(
                            name="direction",
                            comparer=None,
                            key_types=lambda key, value: key in ("down", "up"),
                            value_types=(bool,)
                        ))
                    ]),
                    ("sound", str, None),
                    ("textures", (str, dict), [
                        (lambda key, value: isinstance(value, str), None),
                        (lambda key, value: isinstance(value, dict), Comparer.DictComparerSection(
                            name="direction",
                            comparer=None,
                            key_types=lambda key, value: key in ("down", "east", "north", "side", "south", "up", "west"),
                            value_types=(str,)
                        ))
                    ])
                ]
            )
        )
    )
)

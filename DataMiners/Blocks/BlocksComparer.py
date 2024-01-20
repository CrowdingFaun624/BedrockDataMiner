from typing import TYPE_CHECKING

import Comparison.Comparer as Comparer
import DataMiners.DataMinerTyping as DataMinerTyping

if TYPE_CHECKING:
    import Utilities.Version as Version
    import DataMiners.DataMiner as DataMiner

def normalize(data:DataMinerTyping.MyBlocks, version:"Version.Version", dataminers:dict[str,"DataMiner.DataMinerCollection"]) -> DataMinerTyping.NormalizedBlocks:
    def fix_properties(properties:DataMinerTyping.MyBlocksJsonBlockTypedDict) -> DataMinerTyping.MyBlocksJsonBlockTypedDict:
        for resource_pack_name, resource_pack_properties in properties.items():
            if "sounds" in resource_pack_properties: del resource_pack_properties["sounds"] # MCPE-76182
        return properties
    resource_packs:list[DataMinerTyping.ResourcePackTypedDict] = dataminers["resource_packs"].get_data_file(version, True)
    output = {datum["name"]: Comparer.collapse_resource_packs(fix_properties(datum["properties"]), resource_packs, version.name) for datum in data}
    return output

comparer = Comparer.Comparer(
    normalizer=normalize,
    dependencies=["resource_packs"],
    base_comparer_section=Comparer.DictComparerSection(
        name="block",
        key_types=(str,),
        value_types=(dict,),
        comparer=Comparer.DictComparerSection(
            name="resource pack",
            key_types=(str,),
            value_types=(dict,),
            comparer=Comparer.DictComparerSection(
                name="property",
                key_types=lambda key, value: key in ("blockshape", "brightness_gamma", "carried_textures", "defined_in", "isotropic", "sound", "textures"),
                value_types=lambda key, value: isinstance(value, {
                    "blockshape": (str,),
                    "brightness_gamma": (float),
                    "carried_textures": (str, dict),
                    "defined_in": (list,),
                    "isotropic": (bool, dict),
                    "sound": (str,),
                    "textures": (str, dict)
                }[key]),
                comparer=[
                    ("blockshape", None),
                    ("brightness_gamma", None),
                    (lambda key, value: (key == "carried_textures" and isinstance(value, str)), None),
                    (lambda key, value: (key == "carried_textures" and isinstance(value, dict)), Comparer.DictComparerSection(
                        name="direction",
                        comparer=None,
                        key_types=lambda key, value: key in ("down", "east", "north", "side", "south", "up", "west"),
                        value_types=(str,)
                    )),
                    ("defined_in", Comparer.ListComparerSection(
                        name="resource pack",
                        comparer=None,
                        types=(str,),
                        print_flat=True,
                        ordered=False
                    )),
                    (lambda key, value: (key == "isotropic" and isinstance(value, bool)), None),
                    (lambda key, value: (key == "isotropic" and isinstance(value, dict)), Comparer.DictComparerSection(
                        name="direction",
                        comparer=None,
                        key_types=lambda key, value: key in ("down", "up"),
                        value_types=(bool,)
                    )),
                    ("sound", None),
                    (lambda key, value: (key == "textures" and isinstance(value, str)), None),
                    (lambda key, value: (key == "textures" and isinstance(value, dict)), Comparer.DictComparerSection(
                        name="direction",
                        comparer=None,
                        key_types=lambda key, value: key in ("down", "east", "north", "side", "south", "up", "west"),
                        value_types=(str,)
                    ))
                ]
            )
        )
    )
)

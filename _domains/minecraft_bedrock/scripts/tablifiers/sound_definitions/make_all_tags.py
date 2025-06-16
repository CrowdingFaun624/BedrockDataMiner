from typing import Any

import _domains.minecraft_bedrock.scripts.normalizers.collapse_resource_packs as collapse_resource_packs
from Component.ComponentFunctions import component_function

TAG_ORDER:dict[str,int] = {value.name: index for index, value in enumerate (collapse_resource_packs.ResourcePackTag)}

@component_function()
def make_all_tags(data:dict[str,dict[Any,Any]]) -> None:
    all_tag_combinations = sorted(set(",".join(resource_pack["tags"]) for resource_pack in collapse_resource_packs.resource_pack_dict.values()))
    for tag in all_tag_combinations:
        if tag not in data:
            data[tag] = {}

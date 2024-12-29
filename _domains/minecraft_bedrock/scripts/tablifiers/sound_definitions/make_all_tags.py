from typing import Any

import _domains.minecraft_bedrock.scripts.normalizers.collapse_resource_packs.util as collapse_resource_packs

__all__ = ["make_all_tags"]

TAG_ORDER = {value: index for index, value in enumerate ([
    "core",
    "education",
    "experimental",
    "extra",
    "vanity",
])}

def make_all_tags(data:dict[str,dict[Any,Any]]) -> None:
    all_tag_combinations = sorted(set(",".join(resource_pack["tags"]) for resource_pack in collapse_resource_packs.resource_pack_dict.values()))
    for tag in all_tag_combinations:
        if tag not in data:
            data[tag] = {}

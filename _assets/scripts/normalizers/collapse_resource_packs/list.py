from collections import defaultdict
from typing import TypeVar

import _assets.scripts.normalizers.collapse_resource_packs.util as util

a = TypeVar("a")

__all__ = ["collapse_resource_packs_list"]

def collapse_resource_packs_list(data:dict[str,list[a]]) -> dict[str,list[a]]:
    '''
    Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    '''
    output:defaultdict[str,list[a]] = defaultdict(lambda: [])
    for tag_string, resource_pack_list in util.get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: util.resource_pack_order[item])
        for resource_pack in resource_pack_list:
            output[tag_string].extend(data[resource_pack])
    return dict(output)

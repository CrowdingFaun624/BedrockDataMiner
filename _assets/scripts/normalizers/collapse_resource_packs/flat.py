import _assets.scripts.normalizers.collapse_resource_packs.util as util

__all__ = ["collapse_resource_packs_flat"]

def collapse_resource_packs_flat[a](data:dict[str,a]) -> dict[str,a]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.'''
    output:dict[str,a] = {}
    for tag_string, resource_pack_list in util.get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: util.resource_pack_order[item])
        for resource_pack in resource_pack_list:
            output[tag_string] = data[resource_pack]
    return output

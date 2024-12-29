import _domains.minecraft_bedrock.scripts.normalizers.collapse_resource_packs.util as util

__all__ = ["collapse_resource_pack_names"]

def collapse_resource_pack_names(data:list[str]) -> list[str]:
    output:list[str] = []
    exists_in_output:set[int] = set() # set of IDs because values of resource_pack_tag_strings are always the same.
    for properties_resource_pack in data:
        tag_str = util.resource_pack_tag_strings.get(properties_resource_pack)
        if tag_str is None:
            raise util.UnrecognizedPackError(properties_resource_pack, "pack")
        if (tag_str_id := id(tag_str)) not in exists_in_output:
            exists_in_output.add(tag_str_id)
            output.append(tag_str)
    return list(reversed(output)) # reversed so it behaves the same as it does before refactor.

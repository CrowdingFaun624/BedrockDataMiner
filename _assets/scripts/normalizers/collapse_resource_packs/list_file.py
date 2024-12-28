from collections import defaultdict

import _assets.scripts.normalizers.collapse_resource_packs.util as util
import Utilities.File as File

__all__ = ["collapse_resource_packs_list"]

def collapse_resource_packs_list[a](data:dict[str,File.AbstractFile[list[a]]]) -> File.FakeFile[dict[str,list[a]]]:
    '''
    Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    '''
    output:defaultdict[str,list[a]] = defaultdict(lambda: [])
    file_hashes:list[int] = []
    for tag_string, resource_pack_list in util.get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: util.resource_pack_order[item])
        for resource_pack in resource_pack_list:
            file = data[resource_pack]
            output[tag_string].extend(file.data)
            file_hashes.append(hash(file))
    return File.FakeFile("combined_file", dict(output), hash(tuple(file_hashes)))

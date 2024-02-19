import json

import DataMiners.DataMiner as DataMiner
import DataMiners.DataMinerTyping as DataMinerTyping
import Utilities.FileManager as FileManager

CORE = "core"
EDUCATION = "education"
EXPERIMENTAL = "experimental"
EXTRA = "extra"
VANITY = "vanity"
RESOUCE_PACK_TAGS = [CORE, EDUCATION, EXPERIMENTAL, EXTRA, VANITY]

def get_resource_pack_order(message:str="resource pack") -> list[str]:
    with FileManager.open_shared_file(FileManager.RESOUCE_PACK_DATA_FILE, "rt") as f:
        data = json.load(f)
    file_name = FileManager.RESOUCE_PACK_DATA_FILE.name
    if not isinstance(data, dict):
        raise TypeError("File \"%s\" is not a dict!" % file_name)
    if "order" not in data:
        raise ValueError("File \"%s\".order does not exist!" % file_name)
    if not isinstance(data["order"], list):
        raise TypeError("File \"%s\".order is not a list!" % file_name)
    if not all(isinstance(name, str) for name in data["order"]):
        non_str_items = [index for index, item in enumerate(data["order"]) if not isinstance(item, str)]
        raise TypeError("File \"%s\".order has an item that is not a str: indexes %s" % (file_name, str(non_str_items)))
    if len(set(data["order"])) != len(data["order"]):
        duplicates_already:set[str] = set()
        duplicates:list[str] = [(name, duplicates_already.add(name))[0] for name in data["order"] if name not in duplicates_already]
        raise ValueError("File \"%s\".order has duplicate items: %s" % (file_name, str(duplicates)))
    if "types" not in data:
        raise ValueError("File \"%s\".types does ont exist!" % file_name)
    if not isinstance(data["types"], dict):
        raise TypeError("File \"%s\".types is not a dict!" % file_name)
    if not all(key in data["order"] for key in data["types"]):
        non_existent_packs = [key for key in data["types"] if key not in data["order"]]
        raise ValueError("File \"%s\".types has an item that is not in \"%s\".order: %s" % (file_name, file_name, str(non_existent_packs)))
    if not all(isinstance(value, list) for value in data["types"].values()):
        non_list_items = [key for key, value in data["types"].items() if not isinstance(value, list)]
        raise TypeError("File \"%s\".types has an item that is not a list: %s" % (file_name, str(non_list_items)))
    if not all(all(isinstance(tag, str) for tag in tags) for tags in data["types"].values()):
        non_str_items = [(key, [index for index, sub_value in value if not isinstance(sub_value, str)]) for key, value in data["types"].items() if any(not isinstance(sub_value, str) for sub_value in value)]
        raise TypeError("File \"%s\".types has an item that has an item that is not a str: %s" % (file_name, non_str_items))

    new_types:dict[str,list[str]] = {}
    for name, tags in data["types"].items():
        new_tags:list[str] = [] # I'm doing this ridiculousness so that I save on memory or something IDK.
        for tag in tags:
            for resource_pack_tag in RESOUCE_PACK_TAGS:
                if tag == resource_pack_tag:
                    new_tags.append(resource_pack_tag)
                    break
            else:
                raise ValueError("File \"%s\".types.%s has an item that is not a valid %s tag: %s" % (file_name, name, message, tag))
        new_types[name] = new_tags
    assert data["types"] == new_types
    data["types"] = new_types # I'm not insane you are
    return data

class ResourcePacksDataMiner(DataMiner.DataMiner):
    
    def activate(self, dependency_data:DataMinerTyping.DependenciesTypedDict) -> list[DataMinerTyping.ResourcePackTypedDict]:
        return super().activate()

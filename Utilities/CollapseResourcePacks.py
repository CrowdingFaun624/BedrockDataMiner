from typing import Any, Callable, TYPE_CHECKING, TypeVar

import DataMiners.ResourcePacks.ResourcePacksDataMiner as ResourcePacksDataMiner

if TYPE_CHECKING:
    import DataMiners.DataMinerTyping as DataMinerTyping

a = TypeVar("a")

def make_interface(has_defined_in_key:bool=True, pack_key:str|list[str]="resource_packs") -> Callable[[dict[str,a],"DataMinerTyping.DependenciesTypedDict"],None]:
    def collapse_resource_packs_interface(data:dict[str,a], dependencies:"DataMinerTyping.DependenciesTypedDict") -> None:
        resource_packs:DataMinerTyping.ResourcePacks|None = None
        if isinstance(pack_key, str):
            resource_packs = dependencies[pack_key]
        else:
            resource_packs = None
            for key in pack_key:
                if key not in dependencies or dependencies[key] is None: continue
                resource_packs = dependencies[key]
                break
        if resource_packs is None:
            resource_packs = [{"name": "vanilla", "path": "resource_packs/vanilla/"}]
        collapse_resource_packs(data, resource_packs, has_defined_in_key)
    return collapse_resource_packs_interface

def make_interface_list(pack_key:str="resource_packs") -> Callable[[list[str],"DataMinerTyping.DependenciesTypedDict"],None]:
    def collapse_resource_packs_interface(data:list[str], dependencies:"DataMinerTyping.DependenciesTypedDict") -> None:
        resource_packs = dependencies[pack_key]
        if resource_packs is None:
            resource_packs:DataMinerTyping.ResourcePacks = [{"name": "vanilla", "path": "resource_packs/vanilla/"}]
        collapse_resource_pack_list(data, resource_packs)
    return collapse_resource_packs_interface

def collapse_resource_packs(data:dict[str,a], resource_packs:list["DataMinerTyping.ResourcePackTypedDict"], add_defined_in:bool=True) -> dict[str,a]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    Also adds a "defined_in" tag to each resource pack's properties unless `add_defined_in` is False.'''
    resource_pack_names = {resource_pack["name"] for resource_pack in resource_packs}
    for properties_resource_pack in data:
        if properties_resource_pack not in resource_pack_names:
            raise KeyError("Unknown resource pack \"%s\"!" % (properties_resource_pack))
    output:dict[str,Any] = {}
    for resource_pack in resource_packs:
        resource_pack_name = resource_pack["name"]
        if resource_pack_name not in data: continue
        tags_str = ",".join(ResourcePacksDataMiner.resource_pack_order["types"][resource_pack_name])
        # tags_str is used as the new key
        if tags_str in output:
            output_location = output[tags_str]
            match output_location:
                case dict():
                    output_location.update(data[resource_pack_name])
                case list():
                    output_location.extend(data[resource_pack_name])
                case _:
                    output[tags_str] = data[resource_pack_name]
            if add_defined_in:
                output[tags_str]["defined_in"].append(resource_pack_name)
        else:
            output[tags_str] = data[resource_pack_name]
            if add_defined_in:
                output[tags_str]["defined_in"] = [resource_pack_name]
        del data[resource_pack_name]
    for key, value in output.items():
        # this weird thing with output is because tags_str can be the same as resource_pack.
        # if they are the same, then it thinks that a resource pack with the education
        # tag has already been in here, so it assumes that and KeyErrors on defined_in
        data[key] = value
    return output

def collapse_resource_pack_list(data:list[str], resource_packs:list["DataMinerTyping.ResourcePackTypedDict"]) -> list[str]:
    resource_pack_names = {resource_pack["name"]: resource_pack for resource_pack in resource_packs}
    for properties_resource_pack in data:
        if properties_resource_pack not in resource_pack_names:
            raise KeyError("Unknown resource pack \"%s\"!" % (properties_resource_pack))
    output:list[str] = []
    exists_in_output:set[str] = set()
    while len(data) > 0:
        properties_resource_pack = data.pop()
        if properties_resource_pack not in resource_pack_names:
            raise KeyError("Unknown resource pack \"%s\"!" % (properties_resource_pack))
        tags_str = ",".join(ResourcePacksDataMiner.resource_pack_order["types"][resource_pack_names[properties_resource_pack]["name"]])
        if tags_str not in exists_in_output:
            output.append(tags_str)
            exists_in_output.add(tags_str)
    for item in output:
        data.append(item)
    return data

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import DataMiners.DataMinerTyping as DataMinerTyping

def collapse_resource_packs(properties:dict[str,Any], resource_packs:list["DataMinerTyping.ResourcePackTypedDict"], add_defined_in:bool=True) -> dict[str,Any]:
    '''Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    Also adds a "defined_in" tag to each resource pack's properties unless `add_defined_in` is False.'''
    output:dict[str,Any] = {}
    resource_pack_names = {resource_pack["name"] for resource_pack in resource_packs}
    for properties_resource_pack in properties:
        if properties_resource_pack not in resource_pack_names:
            raise KeyError("Unknown resource pack \"%s\"!" % (properties_resource_pack))
    for resource_pack in resource_packs:
        if resource_pack["name"] in properties:
            tags_str = ",".join(resource_pack["tags"])
            if tags_str in output:
                if isinstance(output[tags_str], dict):
                    output[tags_str].update(properties[resource_pack["name"]])
                else:
                    output[tags_str] = properties[resource_pack["name"]]
                if add_defined_in:
                    output[tags_str]["defined_in"].append(resource_pack["name"])
            else:
                if add_defined_in:
                    output[tags_str] = properties[resource_pack["name"]]
                    output[tags_str]["defined_in"] = [resource_pack["name"]]
                else:
                    output[tags_str] = properties[resource_pack["name"]]
    return output
# the old normalizer embedded in SoundsJsonDataminer had 16 errors, while this file has 0. Yay!

from typing import Any, Mapping, NotRequired, TypedDict

from Component.ComponentFunctions import component_function
from Domain.Domains import get_domain_from_module
from Serializer.Serializer import Serializer
from Utilities.File import FakeFile, File

domain = get_domain_from_module(__name__)
json_serializer = domain.script_referenceable.get_future("minecraft_common!serializers/json", Serializer)


# input


class SoundTypedDict(TypedDict):
    sound: NotRequired[str]
    volume: NotRequired[float|list[float]]
    pitch: NotRequired[float|list[float]]

class VariantsTypedDict(TypedDict):
    key: str
    map: dict[str, "CollectionTypedDict"]

type SoundType = str|SoundTypedDict|dict[str,str|SoundTypedDict]
# represents the possibility of being a regular collection or an interactive collection

class CollectionTypedDict(TypedDict):
    base: NotRequired[str]
    volume: NotRequired[float|list[float]]
    pitch: NotRequired[float|list[float]]
    events: NotRequired[dict[str, SoundType]]
    variants: NotRequired[VariantsTypedDict]

class EntitySoundsTypedDict(TypedDict):
    defaults: CollectionTypedDict
    entities: dict[str,CollectionTypedDict]

class InteractiveSoundsTypedDict(TypedDict):
    block_sounds: dict[str, CollectionTypedDict]
    entity_sounds: EntitySoundsTypedDict

class SoundsJsonTypedDict(TypedDict):
    individual_event_sounds: CollectionTypedDict
    block_sounds: dict[str,CollectionTypedDict]
    entity_sounds: EntitySoundsTypedDict
    interactive_sounds: InteractiveSoundsTypedDict

# output

class MyVariantsTypedDict(TypedDict):
    key: dict[str,str]
    map: dict[str, "MyCollectionTypedDict"]

class MyCollectionTypedDict(TypedDict):
    # base, volume, and pitch are each wrapped with a resource pack dict
    base: dict[str,str]
    volume: dict[str,float|list[float]]
    pitch: dict[str,float|list[float]]
    # each event is wrapped with a resource pack dict
    events: dict[str,dict[str, SoundType]]
    # key is mapped with a resource pack dict. Map is treated as a collections.
    variants: MyVariantsTypedDict

class MyEntitySoundsTypedDict(TypedDict):
    defaults: MyCollectionTypedDict
    entities: dict[str,MyCollectionTypedDict]

class MyInteractiveSoundsTypedDict(TypedDict):
    block_sounds: dict[str, MyCollectionTypedDict]
    entity_sounds: MyEntitySoundsTypedDict

class MySoundsJsonTypedDict(TypedDict):
    individual_event_sounds: MyCollectionTypedDict
    block_sounds: dict[str,MyCollectionTypedDict]
    entity_sounds: MyEntitySoundsTypedDict
    interactive_sounds: MyInteractiveSoundsTypedDict

def merge_collection(pack_name:str, destination:MyCollectionTypedDict, source:CollectionTypedDict) -> None:
    if not set(source.keys()).issubset({"base", "volume", "pitch", "events", "variants"}):
        raise KeyError(f"Weird extra key somewhere in {list(source.keys())}!")
    if "base" in source:
        destination["base"][pack_name] = source["base"]
    if "volume" in source:
        destination["volume"][pack_name] = source["volume"]
    if "pitch" in source:
        destination["pitch"][pack_name] = source["pitch"]
    if "events" in source:
        for event_name, source_event_data in source["events"].items():
            if event_name not in destination["events"]:
                destination["events"][event_name] = {}
            destination["events"][event_name][pack_name] = source_event_data
    if "variants" in source and "key" in source["variants"]:
        destination["variants"]["key"][pack_name] = source["variants"]["key"]
    if "variants" in source and "map" in source["variants"]:
        merge_collections(pack_name, destination["variants"]["map"], source["variants"]["map"])

def merge_collections(pack_name:str, destination:dict[str,MyCollectionTypedDict], source:dict[str,CollectionTypedDict]) -> None:
    for collection_name, source_collection_data in source.items():
        if collection_name not in destination:
            destination[collection_name] = {
                "base": {},
                "volume": {},
                "pitch": {},
                "events": {},
                "variants": {
                    "key": {},
                    "map": {},
                }
            }
        merge_collection(pack_name, destination[collection_name], source_collection_data)

def trace_exists(object:Mapping[str,Any], trace:tuple[str,...]) -> bool:
    '''
    Returns True if the path given by `trace` exists in `object`.
    For example:\n
    .. code-block:: python
        return trace_exists(foo, ["bar", "baz"])
        # will return the same thing as
        return "bar" in foo and "baz" in foo["bar"]
    '''
    for trace_item in trace:
        if trace_item in object:
            object = object[trace_item]
        else: return False
    return True

@component_function(no_arguments=True)
def sounds_json_normalize(data:dict[str,File[SoundsJsonTypedDict]]) -> FakeFile[MySoundsJsonTypedDict]:
    output:MySoundsJsonTypedDict = {
        "individual_event_sounds": {
            "base": {},
            "volume": {}, # must exist to appease pylance
            "pitch": {},
            "events": {},
            "variants": {
                "key": {},
                "map": {},
            },
        },
        "block_sounds": {},
        "entity_sounds": {
            "defaults": {
                "base": {},
                "events": {},
                "volume": {},
                "pitch": {},
                "variants": {
                    "key": {},
                    "map": {},
                },
            },
            "entities": {},
        },
        "interactive_sounds": {
            "block_sounds": {},
            "entity_sounds": {
                "defaults": {
                    "base": {},
                    "events": {},
                    "volume": {},
                    "pitch": {},
                    "variants": {
                        "key": {},
                        "map": {},
                    },
                },
                "entities": {},
            },
        },
    }
    file_hashes:list[int] = []
    for pack_name, sounds_json_file in data.items():
        file_hashes.append(hash(sounds_json_file))
        sounds_json = sounds_json_file.read(json_serializer.get())
        if trace_exists(sounds_json, ("individual_event_sounds",)):
            merge_collection(pack_name, output["individual_event_sounds"], sounds_json["individual_event_sounds"])
        if trace_exists(sounds_json, ("block_sounds",)):
            merge_collections(pack_name, output["block_sounds"], sounds_json["block_sounds"])
        if trace_exists(sounds_json, ("entity_sounds", "defaults")):
            merge_collection(pack_name, output["entity_sounds"]["defaults"], sounds_json["entity_sounds"]["defaults"])
        if trace_exists(sounds_json, ("entity_sounds", "entities")):
            merge_collections(pack_name, output["entity_sounds"]["entities"], sounds_json["entity_sounds"]["entities"])
        if trace_exists(sounds_json, ("interactive_sounds", "block_sounds")):
            merge_collections(pack_name, output["interactive_sounds"]["block_sounds"], sounds_json["interactive_sounds"]["block_sounds"])
        if trace_exists(sounds_json, ("interactive_sounds", "entity_sounds", "defaults")):
            merge_collection(pack_name, output["interactive_sounds"]["entity_sounds"]["defaults"], sounds_json["interactive_sounds"]["entity_sounds"]["defaults"])
        if trace_exists(sounds_json, ("interactive_sounds", "entity_sounds", "entities")):
            merge_collections(pack_name, output["interactive_sounds"]["entity_sounds"]["entities"], sounds_json["interactive_sounds"]["entity_sounds"]["entities"])
    return FakeFile("combined_sounds_json_file", output, None, hash(tuple(file_hashes)))

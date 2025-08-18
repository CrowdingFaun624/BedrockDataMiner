import enum
from collections import defaultdict
from typing import Iterable, Literal, Mapping, Optional, Sequence, TypedDict

from Component.ComponentFunctions import component_function
from Domain.Domains import get_domain_from_module
from Serializer.Serializer import SerializerCreator
from Utilities.Exceptions import StructureException, message
from Utilities.File import AbstractFile, FakeFile
from Utilities.TypeVerifier import (
    EnumTypeVerifier,
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class UnrecognizedPackError(StructureException):
    """
    The behavior pack/resource pack is not recognized.

    :param pack: The name(s) of the behavior pack/resource pack(s).
    :param pack_type: The type of pack ("behavior", "resource", "skin", "emote", "piece", or "pack").
    :param source: The object that found the behavior pack/resource pack.
    :param message: Additional text to place after the main message.
    """

    PACK_TYPES:dict[str,str] = {"behavior": "Behavior pack", "resource": "Resource pack", "skin": "Skin pack", "emote": "Emote directory", "piece": "Piece directory"}

    def __init__(self, pack:str|list[str], pack_type:Literal["behavior", "resource", "skin", "emote", "piece", "pack"], source:Optional[object]=None, message:Optional[str]=None) -> None:
        super().__init__(pack, pack_type, source, message)
        self.pack = pack
        self.pack_type = pack_type
        self.source = source
        self.message = message

    def __str__(self) -> str:
        return f"{self.PACK_TYPES.get(self.pack_type, "Pack")} {f"\"{self.pack}\"" if isinstance(self.pack, str) else f"[{", ".join(f"\"{pack}\"" for pack in self.pack)}]"}{message(self.source, "", ", found by %s,")} is not recognized{message(self.message)}"

class ResourcePackTypedDict(TypedDict):
    name: str
    tags: list[str]

class ResourcePackTag(enum.Enum):
    core = "core"
    education = "education"
    experimental = "experimental"
    extra = "extra"
    vanity = "vanity"

type_verifier = ListTypeVerifier(TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("name", True, str),
    TypedDictKeyTypeVerifier("tags", True, ListTypeVerifier(EnumTypeVerifier(set(tag.name for tag in ResourcePackTag)), list))
), list)

def get_resource_pack_order() -> list[ResourcePackTypedDict]:
    data = get_domain_from_module(__name__).data_files["resource_pack_data"].contents
    type_verifier.verify_throw(data)
    return data

def get_resource_pack_tag_strings() -> dict[str, str]:
    """
    Makes sure that identical strings have the same identity.
    """
    output:dict[str,str] = {}
    already_tags:dict[str,str] = {} # mapping from string to the same string.
    for resource_pack_name, resource_pack in resource_pack_dict.items():
        tag_str = ",".join(resource_pack["tags"])
        if tag_str in already_tags: # evil code
            tag_str = already_tags[tag_str]
        else:
            already_tags[tag_str] = tag_str
        output[resource_pack_name] = tag_str
    return output

resource_pack_data = get_resource_pack_order()
resource_pack_order = {resource_pack["name"]: index for index, resource_pack in enumerate(resource_pack_data)}
resource_pack_dict = {resource_pack_name: resource_pack for resource_pack_name, resource_pack in zip(resource_pack_order, resource_pack_data)}
resource_pack_tag_strings = get_resource_pack_tag_strings()

def get_grouped_resource_packs(data:Iterable[str]) -> Iterable[list[str]]:
    resource_packs_by_tag:defaultdict[str,list[str]] = defaultdict(lambda: [])
    for resource_pack in data:
        tag_string = resource_pack_tag_strings.get(resource_pack)
        if tag_string is None:
            raise UnrecognizedPackError(resource_pack, "pack")
        resource_packs_by_tag[tag_string].append(resource_pack)
    return resource_packs_by_tag.values()

def get_resource_packs_by_tag(data:Iterable[str]) -> Iterable[tuple[str,list[str]]]:
    resource_packs_by_tag:defaultdict[str,list[str]] = defaultdict(lambda: [])
    for resource_pack in data:
        tag_string = resource_pack_tag_strings.get(resource_pack)
        if tag_string is None:
            raise UnrecognizedPackError(resource_pack, "pack")
        resource_packs_by_tag[tag_string].append(resource_pack)
    return resource_packs_by_tag.items()

@component_function(no_arguments=True)
def collapse_resource_packs_dict_old[a](data:Mapping[str,Mapping[str,a]]) -> dict[str,dict[str,a]]:
    """
    Turns keys like {"vanilla", "cartoon"} into resource pack tags, such as {"core", "vanity"}.
    """
    output:defaultdict[str,dict[str,a]] = defaultdict(lambda: {})
    for tag_string, resource_pack_list in get_resource_packs_by_tag(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            output[tag_string].update(data[resource_pack])
    return dict(output)

@component_function(no_arguments=True)
def collapse_resource_packs_dict[a](data:Mapping[str,Mapping[str,a]]) -> dict[tuple[str,...],dict[str,a]]:
    """
    Turns keys like {"vanilla", "vanilla_1.20", "cartoon"} into combined, such as {("vanilla", "vanilla_1.20"), ("cartoon",)}.
    """
    output:dict[tuple[str,...],dict[str,a]] = {}
    for resource_pack_list in get_grouped_resource_packs(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        combined_data:dict[str,a] = {}
        for resource_pack in resource_pack_list:
            combined_data.update(data[resource_pack])
        output[tuple(resource_pack_list)] = combined_data
    return output

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("serializer", True, SerializerCreator),
))
def collapse_resource_packs_dict_file[a](data:Mapping[str,AbstractFile[Mapping[str,a]]], serializer:SerializerCreator) -> FakeFile[dict[tuple[str,...],dict[str,a]]]:
    """
    Turns keys like {"vanilla", "vanilla_1.20", "cartoon"} into combined, such as {("vanilla", "vanilla_1.20"), ("cartoon",)}.
    """
    output:dict[tuple[str,...],dict[str,a]] = {}
    file_hashes:list[int] = []
    for resource_pack_list in get_grouped_resource_packs(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        combined_data:dict[str,a] = {}
        for resource_pack in resource_pack_list:
            file = data[resource_pack]
            file_hashes.append(hash(file))
            combined_data.update(file.read(serializer.serializer))
        output[tuple(resource_pack_list)] = combined_data
    return FakeFile("combined_file", output, None, hash(tuple(file_hashes)))

@component_function(no_arguments=True)
def collapse_resource_packs_flat[a](data:Mapping[str,a]) -> dict[str,a]:
    """
    Turns keys like {"vanilla", "vanilla_1.20", "cartoon"} into combined, such as {("vanilla", "vanilla_1.20"), ("cartoon",)}.
    """
    output:dict[str,a] = {}
    for resource_pack_list in get_grouped_resource_packs(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        for resource_pack in resource_pack_list:
            output[resource_pack] = data[resource_pack]
    return output

@component_function(type_verifier=TypedDictTypeVerifier(
    TypedDictKeyTypeVerifier("serializer", True, SerializerCreator),
))
def collapse_resource_packs_list_file[a](data:Mapping[str,AbstractFile[Sequence[a]]], serializer:SerializerCreator) -> FakeFile[dict[tuple[str,...],list[a]]]:
    """
    Turns keys like {"vanilla", "vanilla_1.20", "cartoon"} into combined, such as {("vanilla", "vanilla_1.20"), ("cartoon",)}.
    """
    output:dict[tuple[str,...],list[a]] = {}
    file_hashes:list[int] = []
    for resource_pack_list in get_grouped_resource_packs(data):
        resource_pack_list.sort(key=lambda item: resource_pack_order[item])
        combined_data:list[a] = []
        for resource_pack in resource_pack_list:
            file = data[resource_pack]
            file_hashes.append(hash(file))
            combined_data.extend(file.read(serializer.serializer))
        output[tuple(resource_pack_list)] = combined_data
    return FakeFile("combined_file", output, None, hash(tuple(file_hashes)))

@component_function(no_arguments=True)
def collapse_resource_pack_names(data:Sequence[str]) -> list[tuple[str,...]]:
    # weird dict thing to deduplicate
    return list(tuple({pack: None for pack in item}) for item in get_grouped_resource_packs(data))

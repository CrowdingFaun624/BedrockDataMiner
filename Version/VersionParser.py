import json
from typing import Any, Mapping, Sequence, TypedDict

from typing_extensions import NotRequired, Required

import Utilities.FileManager as FileManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.Version as Version
import Version.VersionFileType as VersionFileType
import Version.VersionTags as VersionTags


class VersionTypedDict(TypedDict):
    id: Required[str]
    files: Required[dict[str,dict[str,Any]]]
    parent: Required[str|None]
    time: Required[str|None]
    tags: Required[list[str]]
    development_categories: NotRequired[list[str]]
    wiki_page: NotRequired[str]

def is_sorted(data:Sequence[str]) -> tuple[bool, str]:
    return all(a <= b for a, b in zip(data, data[1:])), "data is not sorted!"

def is_sorted_and_not_empty(data:Sequence[str]) -> tuple[bool, str]:
    if len(data) == 0:
        return False, "data is empty!"
    return all(a <= b for a, b in zip(data, data[1:])), "data is not sorted!"

KEY_ORDER = ["id", "files", "parent", "time", "tags", "wiki_page", "development_categories"]
def keys_in_order(data:Mapping[Any, Any]) -> tuple[bool, str]:
    return list(data.keys()) == [key for key in KEY_ORDER if key in data], "keys are not in order of %s!" % (KEY_ORDER)

versions_type_verifier = TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
    TypeVerifier.TypedDictKeyTypeVerifier("id", "a str", True, str),
    TypeVerifier.TypedDictKeyTypeVerifier("files", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.DictTypeVerifier(dict, str, dict, "a dict", "a str", "a dict"), "a dict", "a str", "a dict")),
    TypeVerifier.TypedDictKeyTypeVerifier("parent", "a str or None", True, (str, type(None))),
    TypeVerifier.TypedDictKeyTypeVerifier("time", "a str or None", True, (str, type(None))),
    TypeVerifier.TypedDictKeyTypeVerifier("tags", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", additional_function=is_sorted)),
    TypeVerifier.TypedDictKeyTypeVerifier("wiki_page", "a str", False, str),
    TypeVerifier.TypedDictKeyTypeVerifier("development_categories", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list", additional_function=is_sorted_and_not_empty)),
    function=keys_in_order,
), list, "a dict", "a list")

def verify_data_types(data:list[VersionTypedDict]) -> None:
    '''Raises a TypeError if the structure of `versions.json` is invalid.'''
    versions_type_verifier.base_verify(data)

def read_versions_file() -> list[VersionTypedDict]:
    '''Returns the contents of versions.json'''
    path = FileManager.VERSIONS_FILE
    with open(path, "rt") as f:
        return json.load(f)

def assign_parents(versions:dict[str,Version.Version]) -> None:
    '''Calls `assign_parent` on all versions, giving them a link to another version.'''
    for version in versions.values():
        version.assign_parent(versions)

def verify_ordering(versions:dict[str,Version.Version], version_tags:VersionTags.VersionTags) -> None:
    '''Raises a ValueError if the ordering of the versions is incorrect in any way.'''
    ORDERING_TAGS = version_tags.order.order_tags
    ORDER = version_tags.order.order
    ALLOWED_CHILDREN = version_tags.order.allowed_children
    TOP_LEVEL_TAG = version_tags.order.top_level_tag
    BEFORE_TAGS = version_tags.order.tags_before_top_level_tag
    AFTER_TAGS = version_tags.order.tags_after_top_level_tag

    top_level_versions:list[Version.Version] = [] # versions with no parents
    for version in versions.values():
        if (order_tag_count := sum(order_tag in version.tags for order_tag in ORDERING_TAGS)) != 1:
            if order_tag_count < 1: raise ValueError("Version %s has no ordering tags!" % version.name)
            else: raise ValueError("Version %s has too many ordering tags (>1)!" % version.name)
        if version.parent is None:
            top_level_versions.append(version)

    top_level_childrens:list[Version.Version] = []
    for version in top_level_versions:
        top_level_childrens.extend(version.get_children_recursive())
    if len(set(top_level_childrens)) != len(top_level_childrens):
        already_seen_versions:set[Version.Version] = set()
        for version in top_level_childrens:
            if version in already_seen_versions: raise ValueError("Version \"%s\" is a child of multiple top-level versions!")
            else: already_seen_versions.add(version)
        else: raise ValueError("A duplicate version exists, but unable to find it!")

    for version in top_level_versions:
        if TOP_LEVEL_TAG not in version.tags:
            raise ValueError("Version \"%s\" is a top-level version but is not %s!" % (version.name, TOP_LEVEL_TAG))
    for version in versions.values():
        version_order_tag = version.ordering_tag
        assert version_order_tag is not None
        for child in version.children:
            child_order_tag = child.ordering_tag
            if child_order_tag not in ALLOWED_CHILDREN[version_order_tag]:
                raise ValueError("Version \"%s\" (type \"%s\"), child of \"%s\" (type \"%s\") is not a valid child type of a \"%s\"!"% (child.name, child_order_tag, version.name, version_order_tag, version_order_tag))

    def order_contains_at_index(ordering_tag:VersionTags.VersionTag) -> bool:
        order_at_index = ORDER[order_index]
        if isinstance(order_at_index, set):
            return ordering_tag in order_at_index
        else:
            return ordering_tag == order_at_index

    for version in versions.values():
        order_index = 0
        for child in version.children:
            assert child.ordering_tag is not None
            while not order_contains_at_index(child.ordering_tag):
                order_index += 1
                if order_index >= len(ORDER):
                    raise ValueError("Version \"%s\"'s children, %s, are in an invalid order at child \"%s\"!" % (version.name, str([child.ordering_tag for child in version.children]), child.name))
            # after this while loop, `order_index` must be a value such that child.ordering_tag == or in ORDER[order_index].
    for version in versions.values():
        previous_time = None
        previous_child = None # for error messages
        for child in version.children:
            if child.ordering_tag in BEFORE_TAGS:
                if version.time is not None and child.time is not None and child.time > version.time:
                    raise ValueError("Child \"%s\" (type \"%s\") of \"%s\" (type \"%s\") comes after the latter!" % (child.name, child.ordering_tag, version.name, version.ordering_tag))
            elif child.ordering_tag in AFTER_TAGS:
                if version.time is not None and child.time is not None and child.time < version.time:
                    raise ValueError("Child \"%s\" (type \"%s\") of \"%s\" (type \"%s\") comes before the latter!" % (child.name, child.ordering_tag, version.name, version.ordering_tag))
            if previous_time is not None:
                if child.time is not None and child.time < previous_time:
                    previous_child_name = None if previous_child is None else previous_child.name
                    raise ValueError("Child \"%s\"'s date (\"%s\") comes after child \"%s\"'s date (\"%s\") despite being before it in the children of \"%s\"!" % (previous_child_name, previous_time, child.name, child.time, version.name))
            previous_time = child.time
            previous_child = child

def assign_wiki_pages(versions:dict[str,Version.Version], version_tags:VersionTags.VersionTags) -> None:
    '''Calls `assign_wiki_page` on all versions.'''
    for version in versions.values():
        version.assign_wiki_page(version_tags)

def assign_latest(versions:dict[str,Version.Version], version_tags:VersionTags.VersionTags) -> None:
    for latest_slot, latest_slot_tags in version_tags.latest.latest_tags.items():
        for version in reversed(versions.values()):
            if version.ordering_tag in latest_slot_tags and len(version.version_files) > 0:
                version.latest = True
                if version.parent is not None:
                    version.parent.latest = True
                break

def assign_additional_tags(versions:dict[str,Version.Version], version_tags:VersionTags.VersionTags) -> None:
    '''Assigns tags that are assigned by the VersionParser'''
    for version in versions.values():
        for tag in version_tags.auto_assign_tags:
            tag.auto_assign(version, versions)

def assign_accessors(versions:dict[str,Version.Version], version_file_types:dict[str,VersionFileType.VersionFileType], version_tags:VersionTags.VersionTags) -> None:
    for version in versions.values():
        version.assign_files(version_file_types, version_tags)

def parse() -> tuple[dict[str,Version.Version], VersionTags.VersionTags]:
    data = read_versions_file()
    verify_data_types(data)
    versions:dict[str,Version.Version] = {}
    version_tags = VersionTags.version_tags
    version_file_types = VersionFileType.version_file_types
    for index, version_dict in enumerate(data):
        id = version_dict["id"]
        files = version_dict["files"]
        parent = version_dict["parent"]
        time = version_dict["time"]
        tags = version_dict["tags"]
        wiki_page = version_dict.get("wiki_page", None)
        development_categories = version_dict.get("development_categories")
        if id in versions:
            raise KeyError("Version named \"%s\" already exists!" % id)

        versions[id] = Version.Version(id, files, parent, time, tags, index, version_tags, version_file_types, wiki_page, development_categories)

    assign_parents(versions)
    verify_ordering(versions, version_tags)
    assign_additional_tags(versions, version_tags)
    assign_wiki_pages(versions, version_tags)
    assign_latest(versions, version_tags)
    assign_accessors(versions, version_file_types, version_tags)
    fix_folders(versions)
    return versions, version_tags

def fix_folders(versions:dict[str,Version.Version]) -> None:
    '''Makes folders that are empty and don't exist disappear.
    It is for scenarios like when a version is delayed and betas suddenly point to a new parent,
    or when a version is renamed.'''
    for version_folder in FileManager.VERSIONS_FOLDER.iterdir():
        if not version_folder.is_dir(): continue
        if version_folder.name not in versions:
            try:
                version_folder.rmdir()
            except OSError:
                print("Version folder \"%s\" does not exist in versions.json and contains files!" % version_folder.name)
                continue

versions, version_tags = parse()

def main() -> None:
    parse()

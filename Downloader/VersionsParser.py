import json
from typing import Any, Iterable

import Utilities.FileManager as FileManager
import Utilities.Version as Version
import Utilities.VersionTags as VersionTags

def read_versions_file() -> Any:
    '''Returns the contents of '''
    path = FileManager.VERSIONS_FILE
    with open(path, "rt") as f:
        return json.load(f)
    
def verify_data_types(data:list[dict[str,str|list[str]]]) -> None:
    '''Raises a TypeError if the structure of `versions.json` is invalid.'''
    VALID_KEYS = ["id", "download", "parent", "time", "tags"]
    NoneType = type(None)
    KEY_TYPES = {"id": str, "download": [NoneType, str], "parent": [NoneType, str], "time": [NoneType, str], "tags": list}
    if not isinstance(data, list): raise TypeError("`data` is not a `list`!")
    for index, version_dict in enumerate(data):
        if not isinstance(version_dict, dict): raise TypeError("Item %i of `data` is not a `dict`!" % index)
        keys = list(version_dict.keys())
        if set(keys) != set(VALID_KEYS):
            if "id" in version_dict and isinstance(version_dict["id"], str):
                raise TypeError("Invalid set of keys in version %s of `data`!" % keys["id"])
            else:
                raise TypeError("Invalid set of keys in item %i of `data`!" % index)
        version_name = version_dict["id"]
        if keys != VALID_KEYS:
            raise TypeError("Keys \"%s\" are not in order in version %s of `data`!" % (str(keys), version_name))
        
        for key, key_type in KEY_TYPES.items():
            if isinstance(key_type, Iterable):
                if not any(isinstance(key, key_subtype) for key_subtype in key_type):
                    raise TypeError("Key \"%s\" of version %s of `data` is not any of %s!" % (key, version_name, str(key_type)))
            else:
                if not isinstance(version_dict[key], key_type):
                    raise TypeError("Key \"%s\" of version %s of `data` is not a %s!" % (key, version_name, str(key_type)))
        for tag_index, tag in enumerate(version_dict["tags"]):
            if not isinstance(tag, str):
                raise TypeError("Tag %i of version %s of `data` is not a str!" % (tag_index, version_name))
        if not all(a <= b for a, b in zip(version_dict["tags"], version_dict["tags"][1:])): # if the tags aren't sorted
            raise TypeError("Tags in version \"%s\" of `data` is not sorted!" % version_name)

def assign_parents(versions:list[Version.Version]) -> None:
    '''Calls `assign_parent` on all versions, giving them a link to another version.'''
    versions_dict = {version.name: version for version in versions}
    for version in versions:
        version.assign_parent(versions_dict)

def verify_ordering(versions:list[Version.Version]) -> None:
    '''Raises a ValueError if the ordering of the versions is incorrect in any way.'''
    ORDERING_TAGS = set(VersionTags.order_tags)
    ORDER = [VersionTags.BETA, VersionTags.MAJOR, {VersionTags.MINOR, VersionTags.PATCH, VersionTags.REUPLOAD}]
    ALLOWED_CHILDREN = {
        VersionTags.BETA: [VersionTags.REUPLOAD],
        VersionTags.MAJOR: [VersionTags.BETA, VersionTags.MINOR, VersionTags.PATCH, VersionTags.REUPLOAD],
        VersionTags.MINOR: [VersionTags.BETA, VersionTags.PATCH, VersionTags.REUPLOAD],
        VersionTags.PATCH: [VersionTags.REUPLOAD],
        VersionTags.REUPLOAD: []}
    TOP_LEVEL_TAG = VersionTags.MAJOR
    BEFORE_TAGS = [VersionTags.BETA]
    AFTER_TAGS = [VersionTags.MINOR, VersionTags.PATCH, VersionTags.REUPLOAD]

    for version in versions:
        if (order_tag_count := sum(order_tag in version.tags for order_tag in ORDERING_TAGS)) != 1:
            if order_tag_count < 1: raise ValueError("Version %s has no ordering tags!" % version.name)
            else: raise ValueError("Version %s has too many ordering tags (>1)!" % version.name)
    
    top_level_versions = [version for version in versions if version.parent is None] # versions with no parents
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
    for version in versions:
        version_order_tag = version.ordering_tag
        for child in version.children:
            child_order_tag = child.ordering_tag
            if child_order_tag not in ALLOWED_CHILDREN[version_order_tag]:
                raise ValueError("Version \"%s\" (type \"%s\"), child of \"%s\" (type \"%s\") is not a valid child type of a \"%s\"!"% (child.name, child_order_tag, version.name, version_order_tag, version_order_tag))
    def order_contains_at_index(ordering_tag:VersionTags.VersionTag) -> bool:
        return (not isinstance(ORDER[order_index], Iterable) and ordering_tag == ORDER[order_index]) or (isinstance(ORDER[order_index], Iterable) and ordering_tag in ORDER[order_index])
    for version in versions:
        order_index = 0
        for child in version.children:
            while not order_contains_at_index(child.ordering_tag):
                order_index += 1
                if order_index >= len(ORDER):
                    raise ValueError("Version \"%s\"'s children, %s, are in an invalid order at child \"%s\"!" % (version.name, str([child.ordering_tag for child in version.children]), child.name))
            # after this while loop, `order_index` must be a value such that child.ordering_tag == or in ORDER[order_index].
    for version in versions:
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
                    raise ValueError("Child \"%s\"'s date (\"%s\") comes after child \"%s\"'s date (\"%s\") despite being before it in the children of \"%s\"!" % (previous_child.name, previous_time, child.name, child.time, version.name))
            previous_time = child.time
            previous_child = child

def parse() -> list[Version.Version]:
    data = read_versions_file()
    verify_data_types(data)
    versions:list[Version.Version] = []
    already_names:set[str] = set()
    already_downloads:set[str] = set()
    for index, version_dict in enumerate(data):
        id:str = version_dict["id"]
        download:str|None = version_dict["download"]
        parent:str|None = version_dict["parent"]
        time:str|None = version_dict["time"]
        tags:list[str] = version_dict["tags"]
        versions.append(Version.Version(id, download, parent, time, tags, index))

        if id in already_names:
            raise KeyError("Version named \"%s\" already exists!" % id)
        if download is not None and download in already_downloads:
            raise KeyError("Version with download \"%s\" already exists!" % download)
        already_names.add(id)
        already_downloads.add(download)

    assign_parents(versions)
    verify_ordering(versions)
    return versions

def main() -> None:
    parse()

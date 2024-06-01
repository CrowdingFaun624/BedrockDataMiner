import json
from typing import TYPE_CHECKING, Iterable, TypedDict

from typing_extensions import NotRequired, Required

import Utilities.FileManager as FileManager
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Version.VersionRange as VersionRange

if TYPE_CHECKING:
    import Version.Version as Version

# is_development_tag: Used when comparing to make versions say what they are a development version of.
# is_fork_tag: The version after this one is not a descended from this one. Can be used for April Fools' versions
# is_order_tag: one per version; controls the structure of comparison reports, etc.
# is_major_tag: Used by CompareAll to order the versions.
# auto_assign: assigns this tag to many versions automatically
    # range: object like {"oldest": "version", "newest": "version"}. Use null to represent going to end of versions. Range is [oldest, newest)
# latest_slot: string such as "release" or "development". Exclusive to ordering tags. The newest version with this sort of tag is marked as latest.

class OrderTypedDict(TypedDict):
    order: Required[list[str|list[str]]]
    allowed_children: Required[dict[str,list[str]]]
    top_level_tag: Required[str]
    tags_before_top_level_tag: Required[list[str]]
    tags_after_top_level_tag: Required[list[str]]

class LatestTypedDict(TypedDict):
    latest_slots: list[str]

class AutoAssignRangeTypedDict(TypedDict):
    oldest: Required[str|None]
    newest: Required[str|None]

class AutoAssignTypedDict(TypedDict):
    # one of these keys is required
    range: NotRequired[AutoAssignRangeTypedDict]

class TagTypedDict(TypedDict):
    is_development_tag: NotRequired[bool]
    is_fork_tag: NotRequired[bool]
    is_order_tag: NotRequired[bool]
    is_major_tag: NotRequired[bool]
    latest_slot: NotRequired[str]
    auto_assign: NotRequired[AutoAssignTypedDict]

class VersionTagsJsonTypedDict(TypedDict):
    order: Required[OrderTypedDict]
    latest: Required[LatestTypedDict]
    tags: Required[dict[str,TagTypedDict]]

auto_assigner_typed_dicts = AutoAssignRangeTypedDict

def verify_order_exclusive_keys(data:TagTypedDict) -> tuple[bool, str|None]:
    if data.get("is_order_tag", False):
        pass
    else:
        if "latest_slot" in data:
            return False, "key latest_slot requires is_order_tag to be true!"
        elif "auto_assign" in data:
            return False, "key auto_assign requires is_order_tag to be true!"
        elif "is_major_tag" in data:
            return False, "key is_major_tag requires is_order_tag to be true!"
        elif "is_development_tag" in data:
            return False, "key is_development_tag requires is_order_tag to be true!"
    if "is_development_tag" not in data and "development_name" in data:
        return False, "key development_name requires is_development_tag to be true!"
    return True, None

class AutoAssigner():

    key:str

    def __init__(self, parent_tag:"VersionTag", data:auto_assigner_typed_dicts) -> None:
        self.parent_tag = parent_tag

    def contains_version(self, version:"Version.Version", versions:list["Version.Version"]) -> bool: ...

class AutoAssignerRange(AutoAssigner):

    key = "range"

    def __init__(self, parent_tag:"VersionTag", data:AutoAssignRangeTypedDict) -> None:
        super().__init__(parent_tag, data)
        self.oldest_str = data["oldest"]
        self.newest_str = data["newest"]
        self.version_range:VersionRange.VersionRange|None = None
    
    def get_version(self, version:str, versions:dict[str,"Version.Version"]) -> "Version.Version":
        output = versions.get(version)
        if output is None:
            raise KeyError("VersionTag %s refers to non-existent version \"%s\"!" % (self.parent_tag.name, version))
        return output

    def contains_version(self, version:"Version.Version", versions:dict[str,"Version.Version"]) -> bool:
        if self.version_range is None:
            oldest_version = self.get_version(self.oldest_str, versions) if self.oldest_str is not None else None
            newest_version = self.get_version(self.newest_str, versions) if self.newest_str is not None else None
            self.version_range = VersionRange.VersionRange(oldest_version, newest_version)
        return version in self.version_range

auto_assigners = {auto_assigner.key: auto_assigner for auto_assigner in (AutoAssignerRange,)}

class VersionTag():

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("is_development_tag", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("is_fork_tag", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("is_order_tag", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("is_major_tag", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("development_name", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("latest_slot", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("auto_assign", "a dict", False, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("range", "a dict", False, TypeVerifier.TypedDictTypeVerifier(
                TypeVerifier.TypedDictKeyTypeVerifier("oldest", "a str", True, str),
                TypeVerifier.TypedDictKeyTypeVerifier("newest", "a str", True, str),
            )),
            function=lambda data: (len(data) == 1, "Must have one method of auto assigning")
        )),
        function=verify_order_exclusive_keys, # type: ignore
    )

    def __init__(self, name:str, data:TagTypedDict) -> None:
        self.name = name
        self.is_order_tag = data.get("is_order_tag", False)
        self.is_fork_tag = data.get("is_fork_tag", False)
        self.is_development_tag = data.get("is_development_tag", False)
        self.development_name = data.get("development_name", "dev")
        self.is_major_tag = data.get("is_major", False)
        self.latest_slot = data.get("latest_slot", None)
        self.auto_assign_data = data.get("auto_assign", None)
        self.auto_assign_type = list(self.auto_assign_data.keys())[0] if self.auto_assign_data is not None else None
        self.auto_assigner = auto_assigners[self.auto_assign_type](self, self.auto_assign_data[self.auto_assign_type]) if self.auto_assign_type is not None and self.auto_assign_data is not None else None

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, VersionTag):
            return self.name == value.name
        elif isinstance(value, str):
            return self.name == value
        else:
            return False

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.name)

    def auto_assign(self, version:"Version.Version", versions:dict[str,"Version.Version"]) -> None:
        if self.auto_assigner is None: return
        if self.auto_assigner.contains_version(version, versions):
            version.add_tag(self)

class Latest():

    def __init__(self, data:LatestTypedDict) -> None:
        self.latest_slots = data["latest_slots"]
        self.latest_tags:dict[str,set[VersionTag]] = {latest_slot: set() for latest_slot in self.latest_slots}

    def is_latest_slot(self, slot:str) -> bool:
        return slot in self.latest_slots

    def assign_tags(self, tags:Iterable[VersionTag]) -> None:
        for tag in tags:
            if tag.latest_slot is None: continue
            if not self.is_latest_slot(tag.latest_slot):
                raise ValueError("Latest slot \"%s\" in tag \"%s\" is not recognized!" % (tag.latest_slot, tag.name))
            self.latest_tags[tag.latest_slot].add(tag)

    def __repr__(self) -> str:
        return "<%s [%s]>" % (self.__class__.__name__, ", ".join(self.latest_slots))

class Order():

    def __init__(self, data:OrderTypedDict, tags:dict[str,VersionTag]) -> None:
        self.order_tags = [tag for tag in tags.values() if tag.is_order_tag]
        self.order = self.get_order(data["order"], tags)
        self.top_level_tag = self.get_top_level_tag(data["top_level_tag"], tags)
        self.tags_before_top_level_tag = self.get_tags_in_tag_list(data["tags_before_top_level_tag"], tags)
        self.tags_after_top_level_tag  = self.get_tags_in_tag_list(data["tags_after_top_level_tag"],  tags)
        self.allowed_children = self.get_allowed_children(data["allowed_children"], tags)

    def get_order(self, data:list[str|list[str]], tags:dict[str,VersionTag]) -> list[VersionTag|set[VersionTag]]:
        output:list[VersionTag|set[VersionTag]] = []
        used_tags:set[VersionTag] = set()
        for index, item in enumerate(data):
            if isinstance(item, str):
                tag = tags.get(item, None)
                if tag is None:
                    raise ValueError("Tag \"%s\" in item %i of order does not exist!" % (item, index))
                output.append(tag)
                used_tags.add(tag)
            else:
                tag_set:set[VersionTag] = set()
                for index2, item2 in enumerate(item):
                    tag = tags.get(item2, None)
                    if tag is None:
                        raise ValueError("Tag \"%s\" in item %i of %i of order does not exist!" % (item2, index2, index))
                    tag_set.add(tag)
                    used_tags.add(tag)
                output.append(tag_set)
        for used_tag in used_tags:
            if not used_tag.is_order_tag:
                raise ValueError("Tag \"%s\" is not an order tag and is not allowed in order!" % (used_tag.name))
        if len(used_tags) != len(self.order_tags):
            raise ValueError("Not all order tags were used in order!")
        return output

    def get_top_level_tag(self, top_level_tag:str, tags:dict[str,VersionTag]) -> VersionTag:
        tag = tags.get(top_level_tag, None)
        if tag is None:
            raise ValueError("Tag \"%s\" in top_level_tag does not exist!" % top_level_tag)
        return tag

    def get_tags_in_tag_list(self, data:list[str], tags:dict[str,VersionTag]) -> list[VersionTag]:
        output:list[VersionTag] = []
        for index, item in enumerate(data):
            tag = tags.get(item, None)
            if tag is None:
                raise ValueError("Tag \"%s\" of item %i does not exist!" % (item, index))
            output.append(tag)
        return output

    def get_allowed_children(self, data:dict[str,list[str]], tags:dict[str,VersionTag]) -> dict[VersionTag,list[VersionTag]]:
        output:dict[VersionTag,list[VersionTag]] = {}
        if len(data) != len(self.order_tags):
            raise ValueError("Not all order tags were used in allowed_children!")
        for tag_str, children_str in data.items():
            tag = tags.get(tag_str, None)
            if tag is None:
                raise ValueError("Tag \"%s\" in allowed_children does not exist!" % (tag_str))
            children:list[VersionTag] = []
            for child_str in children_str:
                child = tags.get(child_str, None)
                if child is None:
                    raise ValueError("Tag \"%s\" in key \"%s\" of allowed_children does not exist!" % (child_str))
                children.append(child)
            output[tag] = children
        return output

class VersionTags():

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("order", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("order", "a list or str", True, TypeVerifier.UnionTypeVerifier("a list or str", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
            TypeVerifier.TypedDictKeyTypeVerifier("allowed_children", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"), "a dict", "a str", "a list")),
            TypeVerifier.TypedDictKeyTypeVerifier("top_level_tag", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("tags_before_top_level_tag", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
            TypeVerifier.TypedDictKeyTypeVerifier("tags_after_top_level_tag", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("latest", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("latest_slots", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, dict, "a dict", "a str", "a dict")),
    )

    def __init__(self, data:VersionTagsJsonTypedDict) -> None:
        self.latest = Latest(data["latest"])
        self.tags = self.parse_tags(data["tags"])
        self.latest.assign_tags(self.tags.values())
        self.order = Order(data["order"], self.tags)
        self.auto_assign_tags = [tag for tag in self.tags.values() if tag.auto_assigner is not None]
        if len(self.auto_assign_tags) == 0:
            self.auto_assign_tags = [self.order.top_level_tag]

    def __getitem__(self, tag_name:str) -> VersionTag:
        return self.tags[tag_name]

    def parse_tags(self, data:dict[str,TagTypedDict]) -> dict[str,VersionTag]:
        return {tag_name: VersionTag(tag_name, tag_data) for tag_name, tag_data in data.items()}

def get_ordering_tag(tags:list[VersionTag]) -> VersionTag:
    for tag in tags:
        if tag.is_order_tag:
            return tag
    else:
        raise IndexError("No ordering tags found within list!")

def parse() -> VersionTags:
    with open(FileManager.VERSION_TAGS_FILE, "rt") as f:
        return VersionTags(json.load(f))

version_tags = parse()

from datetime import datetime
from typing import TYPE_CHECKING, Mapping, Sequence

import Domain.Domain as Domain
from Utilities.Exceptions import NoOrderVersionTagsFoundError
from Version.VersionFile import VersionFile
from Version.VersionTag.VersionTag import VersionTag

if TYPE_CHECKING:
    from Downloader.Accessor import Accessor

class Version():

    __slots__ = (
        "_incomplete_tags",
        "_incomplete_tags_dict",
        "_tags",
        "_tags_dict",
        "children",
        "data_directory",
        "domain",
        "full_name",
        "index",
        "latest",
        "name",
        "order_tag",
        "parent",
        "released",
        "time",
        "version_directory",
        "version_files",
        "version_files_dict",
    )

    def __init__(self, name:str, full_name:str, domain:"Domain.Domain", time:datetime|None, index:int) -> None:
        self.name = name
        self.full_name = full_name
        self.time = time
        self.index = index
        self.domain = domain

        self.latest = False
        self.released = True

        self.version_directory = domain.versions_directory.joinpath(self.name)
        self.data_directory = self.version_directory.joinpath("data")
        self.children:list[Version] = []

    def link_finals(
        self,
        parent:"Version|None",
        tags:list[VersionTag],
        version_files:list[VersionFile],
    ) -> None:
        self.parent = parent
        self._incomplete_tags = tags
        self._tags:Sequence[VersionTag]|None = None
        self.version_files = version_files
        self.version_files_dict = {version_file.name: version_file for version_file in self.version_files}
        if self.parent is not None:
            self.parent.children.append(self)

        self._incomplete_tags_dict:dict[str,VersionTag] = {}
        self._tags_dict:Mapping[str,VersionTag]|None = None
        order_tag:VersionTag|None = None
        for tag in self._incomplete_tags:
            self._incomplete_tags_dict[tag.name] = tag
            if order_tag is None and tag.is_order_tag:
                order_tag = tag
            self.released = self.released and not tag.is_unreleased_tag
        if order_tag is None:
            raise NoOrderVersionTagsFoundError(self, self.tags)
        self.order_tag = order_tag

    def _get_tags(self) -> tuple[Sequence[VersionTag], Mapping[str,VersionTag]]:
        tags = self._incomplete_tags.copy()
        for version_tag in self.domain.version_tags.values():
            if version_tag.is_auto_assigned_to(self):
                tags.append(version_tag)
        tags_dict = {tag.name: tag for tag in tags}
        return tags, tags_dict

    @property
    def tags(self) -> Sequence[VersionTag]:
        if self._tags is None or self._tags_dict is None:
            self._tags, self._tags_dict = self._get_tags()
        return self._tags

    @property
    def tags_dict(self) -> Mapping[str,VersionTag]:
        if self._tags is None or self._tags_dict is None:
            self._tags, self._tags_dict = self._get_tags()
        return self._tags_dict

    def get_accessor[a: Accessor](self, file_type:str, required_type:type[a]) -> a|None:
        return self.version_files_dict[file_type].get_accessor(required_type, True)

    def close_accessors(self) -> None:
        for version_file in self.version_files:
            for accessor in version_file.accessors:
                accessor.close()

    def set_constrained_accessor_memory(self, enabled:bool) -> None:
        for version_file in self.version_files:
            for accessor in version_file.accessors:
                if enabled:
                    accessor.constrain_memory()
                else:
                    accessor.constrained_memory = False

    def get_children_recursive(self) -> list["Version"]:
        children = self.children[:]
        for child in self.children:
            children.extend(child.children)
        return children

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

    def __hash__(self) -> int:
        return hash(self.full_name)

    def __lt__(self, other:"Version") -> bool:
        return self.index < other.index

    def __gt__(self, other:"Version") -> bool:
        return self.index > other.index

    def __le__(self, other:"Version") -> bool:
        return self.index <= other.index

    def __ge__(self, other:"Version") -> bool:
        return self.index >= other.index

    def get_referenced_files(self, referenced_files:set[int]) -> None:
        for version_file in self.version_files:
            for accessor in version_file.accessors:
                accessor.get_referenced_files(referenced_files)

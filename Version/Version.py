from datetime import datetime
from typing import TYPE_CHECKING

import Domain.Domain as Domain
from Utilities.Exceptions import NoOrderVersionTagsFoundError
from Version.VersionFile import VersionFile
from Version.VersionTag.VersionTag import VersionTag

if TYPE_CHECKING:
    from Downloader.Accessor import Accessor

class Version():

    __slots__ = (
        "full_name",
        "name",
        "time",
        "index",
        "latest",
        "released",
        "version_directory",
        "data_directory",
        "version_directory",
        "children",
        "parent",
        "tags",
        "tags_dict",
        "version_files",
        "version_files_dict",
        "order_tag",
    )

    def __init__(self, name:str, full_name:str, domain:"Domain.Domain", time:datetime|None, index:int) -> None:
        self.name = name
        self.full_name = full_name
        self.time = time
        self.index = index

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
        self.tags = tags
        self.version_files = version_files
        self.version_files_dict = {version_file.name: version_file for version_file in self.version_files}
        if self.parent is not None:
            self.parent.children.append(self)

        self.tags_dict:dict[str,VersionTag] = {}
        order_tag:VersionTag|None = None
        for tag in self.tags:
            self.tags_dict[tag.name] = tag
            if order_tag is None and tag.is_order_tag:
                order_tag = tag
            self.released = self.released and not tag.is_unreleased_tag
        if order_tag is None:
            raise NoOrderVersionTagsFoundError(self, self.tags)
        self.order_tag = order_tag

    def get_accessor[a: Accessor](self, file_type:str, required_type:type[a]) -> a|None:
        return self.version_files_dict[file_type].get_accessor(required_type, True)

    def close_accessors(self) -> None:
        for version_file in self.version_files:
            for accessor in version_file.accessors:
                accessor.close()

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

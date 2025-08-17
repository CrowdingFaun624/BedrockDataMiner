from datetime import datetime
from typing import TYPE_CHECKING, Mapping, Sequence

from Component.ComponentObject import ComponentObject
from Utilities.Exceptions import NoOrderVersionTagsFoundError
from Utilities.Trace import Trace
from Version.VersionFile import VersionFile, VersionFileCreator
from Version.VersionTag.VersionTag import VersionTag

if TYPE_CHECKING:
    from Downloader.Accessor import Accessor

class Version(ComponentObject):

    __slots__ = (
        "_incomplete_tags",
        "_tags",
        "children",
        "data_directory",
        "index",
        "latest",
        "order_tag",
        "parent",
        "released",
        "time",
        "version_directory",
        "version_file_creators",
        "version_files",
        "version_files_dict",
    )

    def link_version(
        self,
        index:int,
        parent:"Version|None",
        tags:Sequence[VersionTag],
        time:datetime|None,
        version_files:Sequence[VersionFileCreator],
    ) -> None:
        self.latest = False
        self.released = True

        self.version_directory = self.domain.versions_directory.joinpath(self.name)
        self.data_directory = self.version_directory.joinpath("data")
        self.children:list[Version] = []

        self.index = index
        self.parent = parent
        self._incomplete_tags = tags
        self._tags:Sequence[VersionTag]|None = None
        self.time = time
        self.version_file_creators = version_files

    def finalize_version(self, trace:Trace) -> None:
        if self.parent is not None:
            self.parent.children.append(self)

        order_tag:VersionTag|None = None
        for tag in self._incomplete_tags:
            if order_tag is None and tag.is_order_tag:
                order_tag = tag
            self.released = self.released and not tag.is_unreleased_tag
        if order_tag is None:
            raise NoOrderVersionTagsFoundError(self, self._incomplete_tags)
        self.order_tag = order_tag

        self.version_files:Sequence[VersionFile] = [version_file_creator.create_version_file(self) for version_file_creator in self.version_file_creators]
        self.version_files_dict:Mapping[str,VersionFile] = {version_file.name: version_file for version_file in self.version_files}
        del self.version_file_creators

    @property
    def tags(self) -> Sequence[VersionTag]:
        if self._tags is None:
            tags = list(self._incomplete_tags)
            tags.extend(version_tag for version_tag in self.domain.version_tags.values() if version_tag.is_auto_assigned_to(self))
            self._tags = tags
        return self._tags

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

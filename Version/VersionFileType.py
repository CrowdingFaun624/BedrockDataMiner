from typing import TYPE_CHECKING, Sequence

from Component.ComponentObject import ComponentObject

if TYPE_CHECKING:
    from Downloader.AccessorType import AccessorType

class VersionFileType(ComponentObject):

    __slots__ = (
        "allowed_accessor_types",
        "available_when_unreleased",
        "dependencies",
        "must_exist",
    )

    def link_version_file_type(
        self,
        allowed_accessor_types:Sequence["AccessorType"],
        available_when_unreleased:bool,
        dependencies:Sequence["VersionFileType"],
        must_exist:bool,
    ) -> None:
        self.allowed_accessor_types = allowed_accessor_types
        self.available_when_unreleased = available_when_unreleased
        self.dependencies = dependencies
        self.must_exist = must_exist

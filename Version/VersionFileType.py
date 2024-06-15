from typing import TYPE_CHECKING, Any, Optional

import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Downloader.AccessorType as AccessorType

class VersionFileType():

    def __init__(
        self,
        name:str,
        install_location:str,
        must_exist:bool,
        available_when_unreleased:bool,
        has_auto_assign:bool,
        auto_assign_arguments:dict[str,Any]|None,
    ) -> None:
        self.name = name
        self.install_location = install_location
        self.must_exist = must_exist
        self.available_when_unreleased = available_when_unreleased
        self.has_auto_assign = has_auto_assign
        self.auto_assign_arguments = auto_assign_arguments

        self.allowed_accessor_types:list["AccessorType.AccessorType"]|None = None
        self.auto_assign_accessor_type:Optional["AccessorType.AccessorType"] = None

    def link_finals(
        self,
        allowed_accessor_types:list["AccessorType.AccessorType"],
        auto_assign_accessor_type:Optional["AccessorType.AccessorType"]
    ) -> None:
        self.allowed_accessor_types = allowed_accessor_types
        self.auto_assign_accessor_type = auto_assign_accessor_type

    def get_allowed_accessor_types(self) -> list["AccessorType.AccessorType"]:
        if self.allowed_accessor_types is None:
            raise Exceptions.AttributeNoneError("allowed_accessor_types", self)
        return self.allowed_accessor_types

    def get_auto_assign_accessor_type(self) -> "AccessorType.AccessorType":
        if not self.has_auto_assign:
            raise Exceptions.VersionFileTypeNotAutoAssigning(self)
        if self.auto_assign_accessor_type is None:
            raise Exceptions.AttributeNoneError("auto_assign_accessor_type", self)
        return self.auto_assign_accessor_type

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return "<VersionFileType %s>" % (self.name)

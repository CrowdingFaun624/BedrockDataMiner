from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Downloader.AccessorType import AccessorType

class VersionFileType():

    __slots__ = (
        "allowed_accessor_types",
        "available_when_unreleased",
        "full_name",
        "must_exist",
        "name",
    )

    def __init__(
        self,
        name:str,
        full_name:str,
        must_exist:bool,
        available_when_unreleased:bool,
    ) -> None:
        self.name = name
        self.full_name = full_name
        self.must_exist = must_exist
        self.available_when_unreleased = available_when_unreleased

    def link_finals(
        self,
        allowed_accessor_types:list["AccessorType"],
    ) -> None:
        self.allowed_accessor_types = allowed_accessor_types

    def __hash__(self) -> int:
        return hash(self.full_name)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

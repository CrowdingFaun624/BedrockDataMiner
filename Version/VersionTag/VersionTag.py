from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from Version.Version import Version

class VersionTag():

    __slots__ = (
        "auto_assign",
        "development_name",
        "full_name",
        "is_development_tag",
        "is_fork_tag",
        "is_order_tag",
        "is_major_tag",
        "is_unreleased_tag",
        "latest_slot",
        "name",
    )

    def __init__(self, name:str, full_name:str, development_name:str, is_development_tag:bool, is_fork_tag:bool, is_order_tag:bool, is_major_tag:bool, is_unreleased_tag:bool) -> None:
        self.name = name
        self.full_name = full_name
        self.development_name = development_name
        self.is_development_tag = is_development_tag
        self.is_fork_tag = is_fork_tag
        self.is_order_tag = is_order_tag
        self.is_major_tag = is_major_tag
        self.is_unreleased_tag = is_unreleased_tag

        self.latest_slot:str|None = None

    def link_finals(self, latest_slot:str|None, auto_assign:list[Callable[["Version"], bool]]) -> None:
        self.latest_slot = latest_slot
        self.auto_assign = auto_assign

    def is_auto_assigned_to(self, version:"Version") -> bool:
        return any(auto_assigner(version) for auto_assigner in self.auto_assign)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, VersionTag):
            return self.name == value.name
        elif isinstance(value, str):
            return self.name == value
        else:
            return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

    def __hash__(self) -> int:
        return hash(self.full_name)

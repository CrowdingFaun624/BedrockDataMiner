from typing import TYPE_CHECKING, Sequence

from Component.ComponentObject import ComponentObject
from Version.VersionTag.LatestSlot import LatestSlot

if TYPE_CHECKING:
    from Version.Version import Version
    from Version.VersionTag.VersionTagAutoAssigner import VersionTagAutoAssigner


class VersionTag(ComponentObject):

    __slots__ = (
        "auto_assign",
        "development_name",
        "is_development_tag",
        "is_fork_tag",
        "is_order_tag",
        "is_major_tag",
        "is_unreleased_tag",
        "latest_slot",
    )

    def link_version_tag(
        self,
        auto_assign:Sequence["VersionTagAutoAssigner"],
        development_name:str,
        is_development_tag:bool,
        is_fork_tag:bool,
        is_order_tag:bool,
        is_major_tag:bool,
        is_unreleased_tag:bool,
        latest_slot:LatestSlot|None,
    ) -> None:
        self.auto_assign = auto_assign
        self.development_name = development_name
        self.is_development_tag = is_development_tag
        self.is_fork_tag = is_fork_tag
        self.is_order_tag = is_order_tag
        self.is_major_tag = is_major_tag
        self.is_unreleased_tag = is_unreleased_tag
        self.latest_slot = latest_slot

    def is_auto_assigned_to(self, version:"Version") -> bool:
        return any(auto_assigner(version) for auto_assigner in self.auto_assign)

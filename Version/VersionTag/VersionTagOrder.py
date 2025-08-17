from typing import AbstractSet, Mapping, Sequence

from Component.ComponentObject import ComponentObject
from Version.VersionTag.VersionTag import VersionTag


class AllowedChildren(ComponentObject):

    __slots__ = (
        "tag",
        "children",
    )

    def link_allowed_children(
        self,
        children: Sequence[VersionTag],
        tag: VersionTag,
    ) -> None:
        self.children = children
        self.tag = tag

class VersionTagOrder(ComponentObject):

    __slots__ = (
        "allowed_children",
        "allowed_children_list",
        "order",
        "order_list",
        "tags_after_top_level_tag",
        "tags_before_top_level_tag",
        "top_level_tag",
    )

    def link_version_tag_order(
        self,
        allowed_children:Sequence[AllowedChildren],
        order:Sequence[Sequence[VersionTag]],
        tags_after_top_level_tag:Sequence[VersionTag],
        tags_before_top_level_tag:Sequence[VersionTag],
        top_level_tag:VersionTag|None,
    ) -> None:
        self.order_list = order
        self.allowed_children_list = allowed_children
        self.top_level_tag = top_level_tag
        self.tags_before_top_level_tag = tags_before_top_level_tag
        self.tags_after_top_level_tag = tags_after_top_level_tag

    def finalize_version_tag_order(self) -> None:
        self.allowed_children = {allowed_children.tag: allowed_children.children for allowed_children in self.allowed_children_list}
        del self.allowed_children_list
        self.order:Sequence[AbstractSet[VersionTag]] = [set(item) for item in self.order_list]
        del self.order_list

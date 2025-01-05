import Utilities.Exceptions as Exceptions
import Version.VersionTag.VersionTag as VersionTag


class VersionTagOrder():

    __slots__ = (
        "allowed_children",
        "order",
        "tags_after_top_level_tag",
        "tags_before_top_level_tag",
        "top_level_tag",
    )

    def link_finals(
        self,
        order:list[set[VersionTag.VersionTag]],
        allowed_children:dict[VersionTag.VersionTag,list[VersionTag.VersionTag]],
        top_level_tag:VersionTag.VersionTag,
        tags_before_top_level_tag:list[VersionTag.VersionTag],
        tags_after_top_level_tag:list[VersionTag.VersionTag],
    ) -> None:
        self.order = order
        self.allowed_children = allowed_children
        self.top_level_tag = top_level_tag
        self.tags_before_top_level_tag = tags_before_top_level_tag
        self.tags_after_top_level_tag = tags_after_top_level_tag

    def __repr__(self) -> str:
        if self.top_level_tag is None:
            return f"<{self.__class__.__name__} uninitialized>"
        else:
            return f"<{self.__class__.__name__} top: {self.top_level_tag}>"

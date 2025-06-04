from Version.VersionTag.VersionTag import VersionTag


class VersionTagOrder():

    __slots__ = (
        "allowed_children",
        "initialized",
        "order",
        "tags_after_top_level_tag",
        "tags_before_top_level_tag",
        "top_level_tag",
    )

    def __init__(self) -> None:
        self.initialized:bool = False

    def link_finals(
        self,
        order:list[set[VersionTag]],
        allowed_children:dict[VersionTag,list[VersionTag]],
        top_level_tag:VersionTag|None,
        tags_before_top_level_tag:list[VersionTag],
        tags_after_top_level_tag:list[VersionTag],
    ) -> None:
        self.initialized = True
        self.order = order
        self.allowed_children = allowed_children
        self.top_level_tag = top_level_tag
        self.tags_before_top_level_tag = tags_before_top_level_tag
        self.tags_after_top_level_tag = tags_after_top_level_tag

    def __repr__(self) -> str:
        if not self.initialized:
            return f"<{self.__class__.__name__} uninitialized>"
        elif self.top_level_tag is None:
            return f"<{self.__class__.__name__} empty>"
        else:
            return f"<{self.__class__.__name__} top: {self.top_level_tag}>"

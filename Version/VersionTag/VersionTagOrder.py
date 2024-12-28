import Utilities.Exceptions as Exceptions
import Version.VersionTag.VersionTag as VersionTag


class VersionTagOrder():

    def __init__(self) -> None:
        self.order:list[set[VersionTag.VersionTag]]|None = None
        self.allowed_children:dict[VersionTag.VersionTag,list[VersionTag.VersionTag]]|None = None
        self.top_level_tag:VersionTag.VersionTag|None = None
        self.tags_before_top_level_tag:list[VersionTag.VersionTag]|None = None
        self.tags_after_top_level_tag:list[VersionTag.VersionTag]|None = None

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

    def get_order(self) -> list[set[VersionTag.VersionTag]]:
        if self.order is None:
            raise Exceptions.AttributeNoneError("order", self)
        return self.order

    def get_allowed_children(self) -> dict[VersionTag.VersionTag,list[VersionTag.VersionTag]]:
        if self.allowed_children is None:
            raise Exceptions.AttributeNoneError("allowed_children", self)
        return self.allowed_children

    def get_top_level_tag(self) -> VersionTag.VersionTag:
        if self.top_level_tag is None:
            raise Exceptions.AttributeNoneError("top_level_tag", self)
        return self.top_level_tag

    def get_tags_before_top_level_tag(self) -> list[VersionTag.VersionTag]:
        if self.tags_before_top_level_tag is None:
            raise Exceptions.AttributeNoneError("tags_before_top_level_tag", self)
        return self.tags_before_top_level_tag

    def get_tags_after_top_level_tag(self) -> list[VersionTag.VersionTag]:
        if self.tags_after_top_level_tag is None:
            raise Exceptions.AttributeNoneError("tags_after_top_level_tag", self)
        return self.tags_after_top_level_tag

    def __repr__(self) -> str:
        if self.top_level_tag is None:
            return f"<{self.__class__.__name__} uninitialized>"
        else:
            return f"<{self.__class__.__name__} top: {self.top_level_tag}>"

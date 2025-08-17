from Component.ComponentObject import ComponentObject
from Component.Types import register_decorator


@register_decorator(None, ...)
class StructureTag(ComponentObject):

    __slots__ = (
        "is_file",
    )

    def link_structure_tag(self, is_file:bool) -> None:
        self.is_file = is_file

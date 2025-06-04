from Component.Types import register_decorator


@register_decorator(None, ...)
class StructureTag():

    __slots__ = (
        "is_file",
        "name",
    )

    def __init__(self, name:str, is_file:bool) -> None:
        self.name = name
        self.is_file = is_file

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def __hash__(self) -> int:
        return hash(self.name)

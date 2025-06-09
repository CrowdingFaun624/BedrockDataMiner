from Component.Types import register_decorator


@register_decorator(None, ...)
class StructureTag():

    __slots__ = (
        "full_name",
        "is_file",
        "name",
    )

    def __init__(self, name:str, full_name:str, is_file:bool) -> None:
        self.name = name
        self.full_name = full_name
        self.is_file = is_file

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

    def __hash__(self) -> int:
        return hash(self.full_name)

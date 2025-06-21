from Version.Version import Version


class VersionTagAutoAssigner():
    
    __slots__ = (
        "full_name"
    )

    def __init__(self, full_name:str) -> None:
        self.full_name = full_name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

    def __hash__(self) -> int:
        return hash(self.full_name)

    def __call__(self, version:"Version") -> bool:
        ...

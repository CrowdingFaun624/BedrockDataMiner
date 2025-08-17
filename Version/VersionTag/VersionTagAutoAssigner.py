from Component.ComponentObject import ComponentObject
from Version.Version import Version


class VersionTagAutoAssigner(ComponentObject):

    __slots__ = ()

    def __call__(self, version:"Version") -> bool:
        ...

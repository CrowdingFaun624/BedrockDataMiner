from typing import TypedDict

from Component.Component import Component
from Version.VersionTag.VersionTagAutoAssigner import VersionTagAutoAssigner


class VersionTagAutoAssignerTypedDict(TypedDict):
    pass # empty

class VersionTagAutoAssignerComponent[R: VersionTagAutoAssigner, P: VersionTagAutoAssignerTypedDict](Component[R, P]):

    type_name = "VersionTagAutoAssigner"
    object_type = VersionTagAutoAssigner
    abstract = True

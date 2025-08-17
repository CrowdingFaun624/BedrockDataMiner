from typing import TypedDict

from Component.Component import Component
from Version.VersionTag.LatestSlot import LatestSlot


class LatestSlotTypedDict(TypedDict):
    pass # empty

class LatestSlotComponent(Component[LatestSlot, LatestSlotTypedDict]):

    type_name = "LatestSlot"
    object_type = LatestSlot
    abstract = False

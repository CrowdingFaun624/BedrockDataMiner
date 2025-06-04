from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.Pattern import Pattern
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

LATEST_SLOT_PATTERN:Pattern["LatestSlotComponent"] = Pattern("is_latest_slot")

class LatestSlotComponent(Component[str]):

    class_name = "LatestSlot"
    my_capabilities = Capabilities(is_latest_slot=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = ()

    def create_final(self, trace:Trace) -> str:
        return self.name

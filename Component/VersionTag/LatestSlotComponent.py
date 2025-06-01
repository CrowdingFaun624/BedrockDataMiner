import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.Pattern as Pattern
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

LATEST_SLOT_PATTERN:Pattern.Pattern["LatestSlotComponent"] = Pattern.Pattern("is_latest_slot")

class LatestSlotComponent(Component.Component[str]):

    class_name = "LatestSlot"
    my_capabilities = Capabilities.Capabilities(is_latest_slot=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = ()

    def create_final(self, trace:Trace.Trace) -> str:
        return self.name

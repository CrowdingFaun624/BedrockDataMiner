import Component.Capabilities as Capabilities
import Component.Component as Component
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class LatestSlotComponent(Component.Component[str]):

    class_name = "LatestSlot"
    class_name_article = "a LatestSlot"
    my_capabilities = Capabilities.Capabilities(is_latest_slot=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    __slots__ = ()

    def create_final(self) -> None:
        super().create_final()
        self.final = self.name

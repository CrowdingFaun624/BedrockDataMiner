from typing import TYPE_CHECKING

import Component.Capabilities as Capabilties
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Component as Component

class Pattern[a: "Component.Component"]():

    __slots__ = (
        "capability",
        "matching_components",
    )

    def __init__(self, capability:str) -> None:
        '''
        :capabilities: The capability that is matched.
        '''
        if capability not in Capabilties.ALLOWED_CAPABILITIES:
            raise Exceptions.UnrecognizedCapabilityError(capability)
        self.capability = capability
        self.matching_components:set[int]|None = None

    def matches_capabilities(self, capabilities:Capabilties.Capabilities) -> bool:
        return capabilities.capabilities.get(self.capability, False)

    def __contains__(self, capabilities:Capabilties.Capabilities) -> bool:
        if self.matching_components is None:
            import Component.ComponentTypes as ComponentTypes
            self.matching_components = set(
                id(component_type.my_capabilities)
                for component_type in ComponentTypes.component_types
                if self.matches_capabilities(component_type.my_capabilities)
            )
        return id(capabilities) in self.matching_components

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.capability}>"

from typing import TypeIs

from Component.Capabilities import ALLOWED_CAPABILITIES
from Component.Component import Component
from Utilities.Exceptions import UnrecognizedCapabilityError


class Pattern[a: "Component"]():

    __slots__ = (
        "capability",
        "matching_components",
    )

    def __init__(self, capability:str) -> None:
        '''
        :capabilities: The capability that is matched.
        '''
        if capability not in ALLOWED_CAPABILITIES:
            raise UnrecognizedCapabilityError(capability)
        self.capability = capability
        self.matching_components:set[int]|None = None

    def contains(self, component:"Component") -> TypeIs[a]:
        if self.matching_components is None:
            import Component.ComponentTypes as ComponentTypes
            self.matching_components = set(
                id(component_type.my_capabilities)
                for component_type in ComponentTypes.component_types
                if component_type.my_capabilities.capabilities.get(self.capability, False)
            )
        return id(component.my_capabilities) in self.matching_components

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.capability}>"

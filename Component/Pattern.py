from typing import Generic, TypeVar

import Component.Capabilities as Capabilties
import Utilities.Exceptions as Exceptions

a = TypeVar("a")

class Pattern(Generic[a]):

    def __init__(self, capabilities:list[dict[str,bool]]) -> None:
        '''
        For a Pattern to match any Capabilities, it must match one of the Pattern's capability sets (one of the dicts).
        To match a capability set, the Capability must match all existing keys in the capability set.
        Keys that are in the Capabilities but not the capability set do not count for or against it.
        :capabilities: The set of Capabilities that are matched.
        '''
        for capability_set in capabilities:
            for key in capability_set.keys():
                if key not in Capabilties.ALLOWED_CAPABILITIES:
                    raise Exceptions.UnrecognizedCapabilityError(key)
        self.capabilities = capabilities
        self.matching_components:set[int]|None = None

    def matches_capabilities(self, capabilities:Capabilties.Capabilities) -> bool:
        return any(
            all(
                self_capability_set[capability] == capabilities.capabilities.get(capability, None)
                for capability in self_capability_set
            )
            for self_capability_set in self.capabilities
        )

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
        return "<Pattern %s>" % (", ".join("(%s)" % (", ".join("%s: %s" % (capability, value) for capability, value in capability_set.items())) for capability_set in self.capabilities))
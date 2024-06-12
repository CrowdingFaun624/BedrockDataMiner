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

    def __contains__(self, __value: object) -> bool:
        if isinstance(__value, Capabilties.Capabilities):
            for self_capability_set in self.capabilities:
                for capability in self_capability_set:
                    if capability not in __value.capabilities or self_capability_set[capability] != __value.capabilities[capability]:
                        break
                else: # if it never broke, then all capabilities match
                    return True
            return False
        else:
            return NotImplemented

    def __repr__(self) -> str:
        return "<Pattern %s>" % (", ".join("(%s)" % (", ".join("%s: %s" % (capability, value) for capability, value in capability_set.items())) for capability_set in self.capabilities))
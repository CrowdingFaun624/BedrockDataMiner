from typing import Generic, TypeVar

import Component.Capabilities as Capabilties
import Utilities.Exceptions as Exceptions

a = TypeVar("a")

class Pattern(Generic[a]):

    def __init__(self, properties:list[dict[str,bool]]) -> None:
        for property_set in properties:
            for key in property_set.keys():
                if key not in Capabilties.ALLOWED_PROPERTIES:
                    raise Exceptions.UnrecognizedCapabilityError(key)
        self.properties = properties

    def __contains__(self, __value: object) -> bool:
        if isinstance(__value, Capabilties.Capabilities):
            for self_property_set in self.properties:
                for property in self_property_set:
                    if property not in __value.properties or self_property_set[property] != __value.properties[property]:
                        break
                else: # if it never broke, then all properties match
                    return True
            return False
        else:
            return NotImplemented

    def __repr__(self) -> str:
        return "<Pattern %s>" % (", ".join("(%s)" % (", ".join("%s: %s" % (property, value) for property, value in property_set.items())) for property_set in self.properties))
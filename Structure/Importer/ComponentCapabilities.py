ALLOWED_PROPERTIES = set([
    "has_importable_keys", # i.e. TypedDict's importable keys
    "is_base",
    "is_function",
    "is_group",
    "is_structure",
    "is_nbt_base",
    "is_nbt_tag",
    "is_normalizer",
    "is_tag",
    "is_type_alias",
])

class CapabilitiesPattern():

    def __init__(self, properties:list[dict[str,bool]]) -> None:
        for property_set in properties:
            for key in property_set.keys():
                if key not in ALLOWED_PROPERTIES:
                    raise TypeError("Key \"%s\" in properties is not a recognized property!" % (key))
        self.properties = properties
    
    def __contains__(self, __value: object) -> bool:
        if isinstance(__value, Capabilities):
            for self_property_set in self.properties:
                for property in self_property_set:
                    if property not in __value.properties or self_property_set[property] != __value.properties[property]:
                        break
                else: # if it never broke, then all properties match
                    return True
            return False
        else:
            return NotImplemented
    
    def __str__(self) -> str:
        return "<CapabilitiesPattern %s>" % (", ".join("(%s)" % (", ".join("%s: %s" % (property, value) for property, value in property_set.items())) for property_set in self.properties))

class Capabilities():

    def __init__(self, **properties:bool) -> None:
        for key in properties.keys():
            if key not in ALLOWED_PROPERTIES:
                raise KeyError("Key \"%s\" in properties is not a recognized property!" % (key))
        for key in ALLOWED_PROPERTIES:
            if key not in properties:
                properties[key] = False
        self.properties = properties
    
    def __str__(self) -> str:
        return "<Capabilities %s>" % (", ".join(property for property, value in self.properties.items() if value is True))
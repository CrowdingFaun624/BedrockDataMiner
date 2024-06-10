import Utilities.Exceptions as Exceptions

ALLOWED_PROPERTIES = set([
    "has_importable_keys", # i.e. Keymap's importable keys
    "has_keys",
    "is_base",
    "is_dataminer_collection",
    "is_dataminer_settings",
    "is_function",
    "is_group",
    "is_structure",
    "is_nbt_base",
    "is_nbt_tag",
    "is_normalizer",
    "is_tag",
    "is_type_alias",
])

class Capabilities():

    def __init__(self, **properties:bool) -> None:
        for key in properties.keys():
            if key not in ALLOWED_PROPERTIES:
                raise Exceptions.UnrecognizedCapabilityError(key)
        for key in ALLOWED_PROPERTIES:
            if key not in properties:
                properties[key] = False
        self.properties = properties
    
    def __repr__(self) -> str:
        return "<Capabilities %s>" % (", ".join(property for property, value in self.properties.items() if value is True))

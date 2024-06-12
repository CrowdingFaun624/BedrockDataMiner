import Utilities.Exceptions as Exceptions

ALLOWED_CAPABILITIES = set([
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

    def __init__(self, **capabilities:bool) -> None:
        for capability in capabilities.keys():
            if capability not in ALLOWED_CAPABILITIES:
                raise Exceptions.UnrecognizedCapabilityError(capability)
        for capability in ALLOWED_CAPABILITIES:
            if capability not in capabilities:
                capabilities[capability] = False
        self.capabilities = capabilities
    
    def __repr__(self) -> str:
        return "<Capabilities %s>" % (", ".join(property for property, value in self.capabilities.items() if value is True))

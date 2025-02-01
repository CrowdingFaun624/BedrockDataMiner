import Utilities.Exceptions as Exceptions

ALLOWED_CAPABILITIES = set((
    "has_importable_keys", # i.e. Keymap's importable keys
    "has_keys",
    "is_accessor",
    "is_accessor_type",
    "is_base",
    "is_dataminer_collection",
    "is_dataminer_settings",
    "is_file",
    "is_function",
    "is_latest_slot",
    "is_log",
    "is_normalizer",
    "is_primitive",
    "is_serializer",
    "is_structure",
    "is_structure_tag",
    "is_tablifier",
    "is_type_alias",
    "is_union",
    "is_version",
    "is_version_file",
    "is_version_file_type",
    "is_version_tag",
    "is_version_tag_auto_assigner",
    "is_version_tag_order",
))

class Capabilities():

    __slots__ = (
        "capabilities",
    )

    def __init__(self, **capabilities:bool) -> None:
        if len(capabilities) == 0:
            raise Exceptions.EmptyCapabilitiesError(self)
        for capability in capabilities.keys():
            if capability not in ALLOWED_CAPABILITIES:
                raise Exceptions.UnrecognizedCapabilityError(capability)
        for capability in ALLOWED_CAPABILITIES:
            if capability not in capabilities:
                capabilities[capability] = False
        self.capabilities = capabilities

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {", ".join(property for property, value in self.capabilities.items() if value is True)}>"

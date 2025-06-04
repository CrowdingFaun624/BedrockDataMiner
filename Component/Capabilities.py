from Utilities.Exceptions import UnrecognizedCapabilityError

ALLOWED_CAPABILITIES = set((
    "has_importable_keys", # i.e. Keymap's importable keys
    "is_accessor",
    "is_accessor_type",
    "is_base",
    "is_dataminer_collection",
    "is_dataminer_settings",
    "is_filter",
    "is_latest_slot",
    "is_normalizer",
    "is_serializer",
    "is_structure",
    "is_structure_tag",
    "is_type_alias",
    "is_version",
    "is_version_file",
    "is_version_file_type",
    "is_version_tag",
    "is_version_tag_auto_assigner",
))

class Capabilities():

    __slots__ = (
        "capabilities",
    )

    def __init__(self, **capabilities:bool) -> None:
        for capability in capabilities.keys():
            if capability not in ALLOWED_CAPABILITIES:
                raise UnrecognizedCapabilityError(capability)
        for capability in ALLOWED_CAPABILITIES:
            if capability not in capabilities:
                capabilities[capability] = False
        self.capabilities = capabilities

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {", ".join(property for property, value in self.capabilities.items() if value is True)}>"

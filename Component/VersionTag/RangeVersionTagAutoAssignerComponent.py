from typing import TYPE_CHECKING

import Component.ComponentTyping as ComponentTyping
import Component.Version.Field.VersionRangeField as VersionRangeField
import Component.VersionTag.VersionTagAutoAssignerComponent as VersionTagAutoAssignerComponent
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import Component.Version.VersionComponent as VersionComponent

class RangeVersionTagAutoAssignerComponent(VersionTagAutoAssignerComponent.VersionTagAutoAssignerComponent):

    class_name = "RangeVersionTagAutoAssigner"
    class_name_article = "a RangeVersionTagAutoAssigner"
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("newest", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("oldest", "a str or None", True, (str, type(None))),
    )

    def __init__(self, data: ComponentTyping.RangeVersionTagAutoAssignerTypedDict, name: str, component_group: str, index: int | None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.version_range_field = VersionRangeField.VersionRangeField(data["oldest"], data["newest"], [])
        self.fields.extend([self.version_range_field])

    def contains_version(self, version: "VersionComponent.VersionComponent") -> bool:
        return version in self.version_range_field

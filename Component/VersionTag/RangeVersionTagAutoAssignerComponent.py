import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Version.Field.VersionRangeField as VersionRangeField
import Component.Version.VersionComponent as VersionComponent
import Component.VersionTag.VersionTagAutoAssignerComponent as VersionTagAutoAssignerComponent
import Utilities.TypeVerifier as TypeVerifier


class RangeVersionTagAutoAssignerComponent(VersionTagAutoAssignerComponent.VersionTagAutoAssignerComponent):

    class_name = "RangeVersionTagAutoAssigner"
    class_name_article = "a RangeVersionTagAutoAssigner"
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("newest", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("oldest", "a str or None", True, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    __slots__ = (
        "version_range_field",
    )

    def initialize_fields(self, data: ComponentTyping.RangeVersionTagAutoAssignerTypedDict) -> list[Field.Field]:
        self.version_range_field = VersionRangeField.VersionRangeField(data["oldest"], data["newest"], [])
        return [self.version_range_field]

    def contains_version(self, version: "VersionComponent.VersionComponent") -> bool:
        return version in self.version_range_field

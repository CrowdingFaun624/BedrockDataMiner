import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent
import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Utilities.TypeVerifier as TypeVerifier
import Version.VersionFileType as VersionFileType

ACCESSOR_TYPE_PATTERN:Pattern.Pattern["AccessorTypeComponent.AccessorTypeComponent"] = Pattern.Pattern("is_accessor_type")

class VersionFileTypeComponent(Component.Component[VersionFileType.VersionFileType]):

    class_name = "VersionFileType"
    my_capabilities = Capabilities.Capabilities(is_version_file_type=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("allowed_accessor_types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("available_when_unreleased", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("must_exist", "a bool", True, bool),
    )

    __slots__ = (
        "allowed_accessor_types_field",
        "available_when_unreleased",
        "must_exist",
    )

    def initialize_fields(self, data: ComponentTyping.VersionFileTypeTypedDict) -> list[Field.Field]:
        self.must_exist = data["must_exist"]
        self.available_when_unreleased = data["available_when_unreleased"]

        self.allowed_accessor_types_field = ComponentListField.ComponentListField(data["allowed_accessor_types"], ACCESSOR_TYPE_PATTERN, ["allowed_accessor_types"], allow_inline=Field.InlinePermissions.reference, assume_component_group="accessor_types")
        return [self.allowed_accessor_types_field]

    def create_final(self) -> VersionFileType.VersionFileType:
        return VersionFileType.VersionFileType(
            name=self.name,
            must_exist=self.must_exist,
            available_when_unreleased=self.available_when_unreleased,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_finals(
            allowed_accessor_types=list(self.allowed_accessor_types_field.map(lambda accessor_type_component: accessor_type_component.final)),
        )
        return exceptions

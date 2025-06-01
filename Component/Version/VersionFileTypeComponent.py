from typing import Sequence

import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent
import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier
import Version.VersionFileType as VersionFileType

VERSION_FILE_TYPE_PATTERN:Pattern.Pattern["VersionFileTypeComponent"] = Pattern.Pattern("is_version_file_type")

class VersionFileTypeComponent(Component.Component[VersionFileType.VersionFileType]):

    class_name = "VersionFileType"
    my_capabilities = Capabilities.Capabilities(is_version_file_type=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("allowed_accessor_types", True, TypeVerifier.ListTypeVerifier(str, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("available_when_unreleased", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("must_exist", True, bool),
    )

    __slots__ = (
        "allowed_accessor_types_field",
        "available_when_unreleased",
        "must_exist",
    )

    def initialize_fields(self, data: ComponentTyping.VersionFileTypeTypedDict) -> Sequence[Field.Field]:
        self.must_exist = data["must_exist"]
        self.available_when_unreleased = data["available_when_unreleased"]

        self.allowed_accessor_types_field = ComponentListField.ComponentListField(data["allowed_accessor_types"], AccessorTypeComponent.ACCESSOR_TYPE_PATTERN, ("allowed_accessor_types",), allow_inline=Field.InlinePermissions.reference, assume_component_group="accessor_types")
        return (self.allowed_accessor_types_field,)

    def create_final(self, trace:Trace.Trace) -> VersionFileType.VersionFileType:
        return VersionFileType.VersionFileType(
            name=self.name,
            must_exist=self.must_exist,
            available_when_unreleased=self.available_when_unreleased,
        )

    def link_finals(self, trace:Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_finals(
                allowed_accessor_types=list(self.allowed_accessor_types_field.map(lambda accessor_type_component: accessor_type_component.final)),
            )

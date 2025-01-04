from typing import TYPE_CHECKING

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.OptionalComponentField as OptionalComponentField
import Component.Pattern as Pattern
import Utilities.TypeVerifier as TypeVerifier
import Version.VersionFileType as VersionFileType

if TYPE_CHECKING:
    import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent

ACCESSOR_TYPE_PATTERN:Pattern.Pattern["AccessorTypeComponent.AccessorTypeComponent"] = Pattern.Pattern([{"is_accessor_type": True}])

class VersionFileTypeComponent(Component.Component[VersionFileType.VersionFileType]):

    class_name = "VersionFileType"
    class_name_article = "a VersionFileType"
    my_capabilities = Capabilities.Capabilities(is_version_file_type=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("allowed_accessor_types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("auto_assign", "a dict", False, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("accessor_type", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("arguments", "a dict", True, dict),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("available_when_unreleased", "a bool", True, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("install_location", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("must_exist", "a bool", True, bool),
    )

    __slots__ = (
        "allowed_accessor_types_field",
        "auto_assign_accessor_type",
        "auto_assign_arguments",
        "auto_assign_dict",
        "available_when_unreleased",
        "has_auto_assign",
        "install_location",
        "must_exist",
    )

    def initialize_fields(self, data: ComponentTyping.VersionFileTypeTypedDict) -> list[Field.Field]:
        self.install_location = data["install_location"]
        self.must_exist = data["must_exist"]
        self.available_when_unreleased = data["available_when_unreleased"]
        self.has_auto_assign = "auto_assign" in data
        self.auto_assign_arguments = data["auto_assign"]["arguments"] if "auto_assign" in data else None
        self.auto_assign_dict:ComponentTyping.VersionFileTypedDict|None = {"version_file_type": self.name, "accessors": [data["auto_assign"]]} if "auto_assign" in data else None

        self.allowed_accessor_types_field = ComponentListField.ComponentListField(data["allowed_accessor_types"], ACCESSOR_TYPE_PATTERN, ["allowed_accessor_types"], allow_inline=Field.InlinePermissions.reference)
        self.auto_assign_accessor_type = OptionalComponentField.OptionalComponentField(data["auto_assign"]["accessor_type"] if "auto_assign" in data else None, ACCESSOR_TYPE_PATTERN, ["auto_assign", "accessor_type"], allow_inline=Field.InlinePermissions.reference)
        return [self.allowed_accessor_types_field, self.auto_assign_accessor_type]

    def create_final(self) -> None:
        super().create_final()
        self.final = VersionFileType.VersionFileType(
            name=self.name,
            install_location=self.install_location,
            must_exist=self.must_exist,
            available_when_unreleased=self.available_when_unreleased,
            has_auto_assign=self.has_auto_assign,
            auto_assign_arguments=self.auto_assign_arguments
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.get_final().link_finals(
            allowed_accessor_types=list(self.allowed_accessor_types_field.map(lambda accessor_type_component: accessor_type_component.get_final())),
            auto_assign_accessor_type=accessor_type_component.get_final() if (accessor_type_component := self.auto_assign_accessor_type.get_component()) is not None else None,
        )
        return exceptions

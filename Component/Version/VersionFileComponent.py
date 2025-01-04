from typing import TYPE_CHECKING, cast

import Component.Accessor.AccessorComponent as AccessorComponent
import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier
import Version.VersionFile as VersionFile

if TYPE_CHECKING:
    import Component.Version.VersionComponent as VersionComponent
    import Component.Version.VersionFileTypeComponent as VersionFileTypeComponent

ACCESSOR_PATTERN:Pattern.Pattern[AccessorComponent.AccessorComponent] = Pattern.Pattern([{"is_accessor": True}])
VERSION_FILE_TYPE_PATTERN:Pattern.Pattern["VersionFileTypeComponent.VersionFileTypeComponent"] = Pattern.Pattern([{"is_version_file_type": True}])

class VersionFileComponent(Component.Component[VersionFile.VersionFile]):

    class_name = "VersionFile"
    class_name_article = "a VersionFile"
    my_capabilities = Capabilities.Capabilities(is_version_file=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("accessors", "a list", True, TypeVerifier.ListTypeVerifier(dict, list, "a dict", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("version_file_type", "a str", True, str),
    )

    __slots__ = (
        "accessors_field",
        "version_file_type_field",
    )

    def initialize_fields(self, data: ComponentTyping.VersionFileTypedDict) -> list[Field.Field]:
        self.version_file_type_field = ComponentField.ComponentField(data["version_file_type"], VERSION_FILE_TYPE_PATTERN, ["version_file_type"], allow_inline=Field.InlinePermissions.reference)
        self.accessors_field = ComponentListField.ComponentListField(data["accessors"], ACCESSOR_PATTERN, ["accessors"], allow_inline=Field.InlinePermissions.inline, assume_type=AccessorComponent.AccessorComponent.class_name)
        return [self.version_file_type_field, self.accessors_field]

    def create_final(self) -> None:
        super().create_final()
        self.final = VersionFile.VersionFile()

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        version = cast("VersionComponent.VersionComponent", self.get_inline_parent()).get_final()
        self.get_final().link_finals(
            version=version,
            version_file_type=self.version_file_type_field.get_component().get_final(),
            accessors=list(self.accessors_field.map(lambda accessor_component: accessor_component.get_final())),
        )
        return exceptions

    def check(self) -> list[Exception]:
        exceptions = super().check()
        allowed_accessors = set(self.version_file_type_field.get_component().allowed_accessor_types_field.get_components())
        exceptions.extend(
            Exceptions.VersionFileInvalidAccessorError(self.get_final(), accessor.name)
            for accessor in self.accessors_field.get_components()
            if accessor.accessor_type_field.get_component() not in allowed_accessors
        )
        return exceptions

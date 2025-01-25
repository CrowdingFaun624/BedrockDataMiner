from typing import Sequence, cast

import Component.Accessor.AccessorComponent as AccessorComponent
import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Version.VersionComponent as VersionComponent
import Component.Version.VersionFileTypeComponent as VersionFileTypeComponent
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier
import Version.VersionFile as VersionFile

VERSION_FILE_PATTERN:Pattern.Pattern["VersionFileComponent"] = Pattern.Pattern("is_version_file")

class VersionFileComponent(Component.Component[VersionFile.VersionFile]):

    class_name = "VersionFile"
    my_capabilities = Capabilities.Capabilities(is_version_file=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("accessors", True, TypeVerifier.ListTypeVerifier(dict, list)),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("version_file_type", True, str),
    )

    __slots__ = (
        "accessors_field",
        "version_file_type_field",
    )

    def initialize_fields(self, data: ComponentTyping.VersionFileTypedDict) -> Sequence[Field.Field]:
        self.version_file_type_field = ComponentField.ComponentField(data["version_file_type"], VersionFileTypeComponent.VERSION_FILE_TYPE_PATTERN, ("version_file_type",), allow_inline=Field.InlinePermissions.reference, assume_component_group="version_file_types")
        self.accessors_field = ComponentListField.ComponentListField(data["accessors"], AccessorComponent.ACCESSOR_PATTERN, ("accessors",), allow_inline=Field.InlinePermissions.inline, assume_type=AccessorComponent.AccessorComponent.class_name)
        return (self.version_file_type_field, self.accessors_field)

    def create_final(self) -> VersionFile.VersionFile:
        return VersionFile.VersionFile()

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        version = cast("VersionComponent.VersionComponent", self.get_inline_parent()).final
        self.final.link_finals(
            version=version,
            version_file_type=self.version_file_type_field.subcomponent.final,
            accessors=list(self.accessors_field.map(lambda accessor_component: accessor_component.final)),
        )
        return exceptions

    def check(self) -> list[Exception]:
        exceptions = super().check()
        allowed_accessors = set(self.version_file_type_field.subcomponent.allowed_accessor_types_field.subcomponents)
        exceptions.extend(
            Exceptions.VersionFileInvalidAccessorError(self.final, accessor.name)
            for accessor in self.accessors_field.subcomponents
            if accessor.accessor_type_field.subcomponent not in allowed_accessors
        )
        return exceptions

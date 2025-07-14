from typing import TYPE_CHECKING, Sequence, cast

from Component.Accessor.AccessorComponent import ACCESSOR_PATTERN, AccessorComponent
from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import VersionFileTypedDict
from Component.Field.ComponentField import ComponentField
from Component.Field.ComponentListField import ComponentListField
from Component.Field.Field import Field, InlinePermissions
from Component.Pattern import Pattern
from Component.Version.VersionFileTypeComponent import VERSION_FILE_TYPE_PATTERN
from Utilities.Exceptions import VersionFileInvalidAccessorError
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)
from Version.VersionFile import VersionFile

if TYPE_CHECKING:
    from Component.Version.VersionComponent import VersionComponent

VERSION_FILE_PATTERN:Pattern["VersionFileComponent"] = Pattern("is_version_file")

class VersionFileComponent(Component[VersionFile]):

    class_name = "VersionFile"
    my_capabilities = Capabilities(is_version_file=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("accessors", True, ListTypeVerifier(dict, list)),
        TypedDictKeyTypeVerifier("type", False, str),
        TypedDictKeyTypeVerifier("version_file_type", True, str),
    )
    allow_reference_inheritance = False

    __slots__ = (
        "accessors_field",
        "version_file_type_field",
    )

    def initialize_fields(self, data: VersionFileTypedDict) -> Sequence[Field]:
        self.version_file_type_field = ComponentField(data["version_file_type"], VERSION_FILE_TYPE_PATTERN, ("version_file_type",), allow_inline=InlinePermissions.reference)
        self.accessors_field = ComponentListField(data["accessors"], ACCESSOR_PATTERN, ("accessors",), allow_inline=InlinePermissions.inline, assume_type=AccessorComponent.class_name)
        return (self.version_file_type_field, self.accessors_field)

    def create_final(self, trace:Trace) -> VersionFile:
        return VersionFile(
            full_name=self.full_name,
        )

    def link_finals(self, trace:Trace) -> None:
        version = cast("VersionComponent", self.get_inline_parent()).final
        self.final.link_finals(
            version=version,
            version_file_type=self.version_file_type_field.subcomponent.final,
            accessors=list(self.accessors_field.map(lambda accessor_component: accessor_component.final)),
        )

    def check(self, trace:Trace) -> None:
        allowed_accessors = set(self.version_file_type_field.subcomponent.allowed_accessor_types_field.subcomponents)
        trace.exceptions(
            VersionFileInvalidAccessorError(self.final, accessor.name)
            for accessor in self.accessors_field.subcomponents
            if accessor.accessor_type_field.subcomponent not in allowed_accessors
        )

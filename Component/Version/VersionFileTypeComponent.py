from typing import Sequence

from Component.Accessor.AccessorTypeComponent import ACCESSOR_TYPE_PATTERN
from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import VersionFileTypeTypedDict
from Component.Field.ComponentListField import ComponentListField
from Component.Field.Field import Field, InlinePermissions
from Component.Pattern import Pattern
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)
from Version.VersionFileType import VersionFileType

VERSION_FILE_TYPE_PATTERN:Pattern["VersionFileTypeComponent"] = Pattern("is_version_file_type")

class VersionFileTypeComponent(Component[VersionFileType]):

    class_name = "VersionFileType"
    my_capabilities = Capabilities(is_version_file_type=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("allowed_accessor_types", True, ListTypeVerifier(str, list)),
        TypedDictKeyTypeVerifier("available_when_unreleased", True, bool),
        TypedDictKeyTypeVerifier("must_exist", True, bool),
    )

    __slots__ = (
        "allowed_accessor_types_field",
        "available_when_unreleased",
        "must_exist",
    )

    def initialize_fields(self, data: VersionFileTypeTypedDict) -> Sequence[Field]:
        self.must_exist = data["must_exist"]
        self.available_when_unreleased = data["available_when_unreleased"]

        self.allowed_accessor_types_field = ComponentListField(data["allowed_accessor_types"], ACCESSOR_TYPE_PATTERN, ("allowed_accessor_types",), allow_inline=InlinePermissions.reference)
        return (self.allowed_accessor_types_field,)

    def create_final(self, trace:Trace) -> VersionFileType:
        return VersionFileType(
            name=self.name,
            full_name=self.full_name,
            must_exist=self.must_exist,
            available_when_unreleased=self.available_when_unreleased,
        )

    def link_finals(self, trace:Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_finals(
                allowed_accessor_types=list(self.allowed_accessor_types_field.map(lambda accessor_type_component: accessor_type_component.final)),
            )

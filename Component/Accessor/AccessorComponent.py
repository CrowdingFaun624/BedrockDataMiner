from typing import Any, Sequence

import Domain.Domain as Domain
from Component.Accessor.AccessorTypeComponent import ACCESSOR_TYPE_PATTERN
from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import AccessorTypedDict
from Component.Field.ComponentField import ComponentField
from Component.Field.Field import Field
from Component.Pattern import Pattern
from Component.Permissions import InheritancePermissions, InlinePermissions
from Downloader.Accessor import Accessor
from Downloader.AccessorType import AccessorType
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier
from Version.Version import Version
from Version.VersionFile import VersionFile

ACCESSOR_PATTERN:Pattern["AccessorComponent"] = Pattern("is_accessor")

class AccessorCreator():

    __slots__ = (
        "accessor",
        "accessor_type",
        "arguments",
        "domain",
        "full_name",
        "version",
        "version_file",
    )

    def __init__(
        self,
        full_name:str,
        domain:"Domain.Domain",
        arguments:dict[str,Any],
    ) -> None:
        self.full_name = full_name
        self.domain = domain
        self.arguments = arguments

        self.accessor:Accessor|None = None
        self.accessor_type:AccessorType
        self.version:Version
        self.version_file:VersionFile

    def create_accessor(self, trace:Trace) -> Accessor|None:
        if self.accessor is None:
            self.accessor = self.accessor_type.create_accessor(
                full_name=self.full_name,
                trace=trace,
                version=self.version,
                domain=self.domain,
                file_type=self.version_file.version_file_type,
                instance_arguments=self.arguments
            )
        return self.accessor

    def link(
        self,
        accessor_type:AccessorType,
        version:Version,
        version_file:VersionFile,
    ) -> None:
        self.accessor_type = accessor_type
        self.version = version
        self.version_file = version_file

class AccessorComponent(Component[AccessorCreator]):

    class_name = "Accessor"
    my_capabilities = Capabilities(is_accessor=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("accessor_type", True, str),
        TypedDictKeyTypeVerifier("arguments", True, dict),
        TypedDictKeyTypeVerifier("type", False, str),
    )
    inline_permissions = InlinePermissions.inline
    inheritance_permissions = InheritancePermissions.normal

    __slots__ = (
        "arguments",
        "accessor_type_field",
    )

    def initialize_fields(self, data: AccessorTypedDict) -> Sequence[Field]:
        self.arguments = data["arguments"]
        self.accessor_type_field = ComponentField(data["accessor_type"], ACCESSOR_TYPE_PATTERN, ("accessor_type",))
        return (self.accessor_type_field,)

    def create_final(self, trace:Trace) -> AccessorCreator:
        return AccessorCreator(
            self.full_name,
            self.domain,
            self.arguments
        )

    def link_finals(self, trace: Trace) -> None:
        self.final.link(
            accessor_type=self.accessor_type_field.subcomponent.final,
            version=self.get_inline_parent().get_inline_parent().final,
            version_file=self.get_inline_parent().final,
        )

from typing import TYPE_CHECKING, Any, Sequence, cast

import Domain.Domain as Domain
from Component.Accessor.AccessorTypeComponent import (
    ACCESSOR_TYPE_PATTERN,
    AccessorTypeComponent,
)
from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentTyping import AccessorTypedDict
from Component.Field.ComponentField import ComponentField
from Component.Field.Field import Field, InlinePermissions
from Component.Pattern import Pattern
from Downloader.Accessor import Accessor
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

if TYPE_CHECKING:
    from Component.Version.VersionComponent import VersionComponent
    from Component.Version.VersionFileComponent import VersionFileComponent

ACCESSOR_PATTERN:Pattern["AccessorComponent"] = Pattern("is_accessor")

class AccessorCreator():

    __slots__ = (
        "accessor",
        "accessor_type_field",
        "arguments",
        "domain",
        "full_name",
        "version_component",
        "version_file_component",
    )

    def __init__(
        self,
        full_name:str,
        domain:"Domain.Domain",
        version_file_component:"VersionFileComponent",
        version_component:"VersionComponent",
        accessor_type_field:ComponentField["AccessorTypeComponent"],
        arguments:dict[str,Any],
    ) -> None:
        self.full_name = full_name
        self.domain = domain
        self.version_file_component = version_file_component
        self.version_component = version_component
        self.accessor_type_field = accessor_type_field
        self.arguments = arguments
        self.accessor:Accessor|None = None

    def create_accessor(self, trace:Trace) -> Accessor|None:
        if self.accessor is None:
            self.accessor = self.accessor_type_field.subcomponent.final.create_accessor(
                full_name=self.full_name,
                trace=trace,
                version=self.version_component.final,
                domain=self.domain,
                file_type=self.version_file_component.version_file_type_field.subcomponent.final,
                instance_arguments=self.arguments
            )
        return self.accessor

    def clear_variables(self) -> None:
        '''Required step for being able to remove all Components after importing is finished.'''
        del self.version_file_component
        del self.version_component
        del self.accessor_type_field

class AccessorComponent(Component[AccessorCreator]):

    class_name = "Accessor"
    my_capabilities = Capabilities(is_accessor=True)
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("accessor_type", True, str),
        TypedDictKeyTypeVerifier("arguments", True, dict),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "arguments",
        "accessor_type_field",
    )

    def initialize_fields(self, data: AccessorTypedDict) -> Sequence[Field]:
        self.arguments = data["arguments"]
        self.accessor_type_field = ComponentField(data["accessor_type"], ACCESSOR_TYPE_PATTERN, ("accessor_type",), allow_inline=InlinePermissions.reference)
        return (self.accessor_type_field,)

    def create_final(self, trace:Trace) -> AccessorCreator:
        return AccessorCreator(
            self.full_name,
            self.domain,
            cast("VersionFileComponent", self.get_inline_parent()), cast("VersionComponent", self.get_inline_parent().get_inline_parent()),
            self.accessor_type_field, self.arguments
        )

    def finalize(self, trace:Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().finalize(trace)
            self.final.create_accessor(trace) # just test errors
            self.final.clear_variables()

from typing import Any, Sequence, cast

import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent
import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Version.VersionComponent as VersionComponent
import Component.Version.VersionFileComponent as VersionFileComponent
import Domain.Domain as Domain
import Downloader.Accessor as Accessor
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

ACCESSOR_PATTERN:Pattern.Pattern["AccessorComponent"] = Pattern.Pattern("is_accessor")

class AccessorCreator():

    __slots__ = (
        "accessor",
        "accessor_type_field",
        "arguments",
        "domain",
        "version_component",
        "version_file_component",
    )

    def __init__(
        self,
        domain:"Domain.Domain",
        version_file_component:"VersionFileComponent.VersionFileComponent",
        version_component:"VersionComponent.VersionComponent",
        accessor_type_field:ComponentField.ComponentField["AccessorTypeComponent.AccessorTypeComponent"],
        arguments:dict[str,Any],
    ) -> None:
        self.domain = domain
        self.version_file_component = version_file_component
        self.version_component = version_component
        self.accessor_type_field = accessor_type_field
        self.arguments = arguments
        self.accessor:Accessor.Accessor|None = None

    def create_accessor(self, trace:Trace.Trace) -> Accessor.Accessor|None:
        if self.accessor is None:
            self.accessor = self.accessor_type_field.subcomponent.final.create_accessor(
                trace,
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

class AccessorComponent(Component.Component[AccessorCreator]):

    class_name = "Accessor"
    my_capabilities = Capabilities.Capabilities(is_accessor=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("accessor_type", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("arguments", True, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "arguments",
        "accessor_type_field",
    )

    def initialize_fields(self, data: ComponentTyping.AccessorTypedDict) -> Sequence[Field.Field]:
        self.arguments = data["arguments"]
        self.accessor_type_field = ComponentField.ComponentField(data["accessor_type"], AccessorTypeComponent.ACCESSOR_TYPE_PATTERN, ("accessor_type",), allow_inline=Field.InlinePermissions.reference, assume_component_group="accessor_types")
        return (self.accessor_type_field,)

    def create_final(self, trace:Trace.Trace) -> AccessorCreator:
        return AccessorCreator(
            self.domain,
            cast("VersionFileComponent.VersionFileComponent", self.get_inline_parent()), cast("VersionComponent.VersionComponent", self.get_inline_parent().get_inline_parent()),
            self.accessor_type_field, self.arguments
        )

    def finalize(self, trace:Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().finalize(trace)
            self.final.create_accessor(trace) # just test errors
            self.final.clear_variables()

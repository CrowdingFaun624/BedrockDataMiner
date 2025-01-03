from typing import TYPE_CHECKING, Any, cast

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Domain.Domain as Domain
import Downloader.Accessor as Accessor
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent
    import Component.Version.VersionComponent as VersionComponent
    import Component.Version.VersionFileComponent as VersionFileComponent

ACCESSOR_TYPE_PATTERN:Pattern.Pattern["AccessorTypeComponent.AccessorTypeComponent"] = Pattern.Pattern([{"is_accessor_type": True}])

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

    def create_accessor(self) -> Accessor.Accessor:
        if self.accessor is None:
            self.accessor = self.accessor_type_field.get_component().get_final().create_accessor(
                version=self.version_component.get_final(),
                domain=self.domain,
                file_type=self.version_file_component.version_file_type_field.get_component().get_final(),
                accessor_arguments=self.arguments,
            )
            self.accessor.initialize()
        return self.accessor
    
    def clear_variables(self) -> None:
        '''Required step for being able to remove all Components after importing is finished.'''
        del self.version_file_component
        del self.version_component
        del self.accessor_type_field

class AccessorComponent(Component.Component[AccessorCreator]):

    class_name = "Accessor"
    class_name_article = "an Accessor"
    my_capabilities = Capabilities.Capabilities(is_accessor=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("accessor_type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("arguments", "a dict", True, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    __slots__ = (
        "arguments",
        "accessor_type_field",
    )

    def initialize_fields(self, data: ComponentTyping.AccessorTypedDict) -> list[Field.Field]:
        self.arguments = data["arguments"]
        self.accessor_type_field = ComponentField.ComponentField(data["accessor_type"], ACCESSOR_TYPE_PATTERN, ["accessor_type"], allow_inline=Field.InlinePermissions.reference)
        return [self.accessor_type_field]

    def create_final(self) -> None:
        super().create_final()
        version_file = self.get_inline_parent()
        self.final = AccessorCreator(self.domain, cast("VersionFileComponent.VersionFileComponent", self.get_inline_parent()), cast("VersionComponent.VersionComponent", version_file.get_inline_parent()), self.accessor_type_field, self.arguments)

    def check(self) -> list[Exception]:
        exceptions = super().check()
        trace = TypeVerifier.make_trace([self.name, self.component_group])
        exceptions.extend(self.accessor_type_field.get_component().get_final().get_parameters().verify(self.arguments, trace))
        return exceptions

    def finalize(self) -> list[Exception]:
        exceptions = super().finalize()
        final = self.get_final()
        final.create_accessor()
        final.clear_variables()
        return exceptions

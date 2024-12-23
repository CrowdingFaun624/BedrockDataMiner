from typing import TYPE_CHECKING, Any, cast

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Downloader.Accessor as Accessor
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

if TYPE_CHECKING:
    import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent
    import Component.Version.VersionComponent as VersionComponent
    import Component.Version.VersionFileComponent as VersionFileComponent

ACCESSOR_TYPE_PATTERN:Pattern.Pattern["AccessorTypeComponent.AccessorTypeComponent"] = Pattern.Pattern([{"is_accessor_type": True}])

class AccessorCreator():

    def __init__(
        self,
        version_file_component:"VersionFileComponent.VersionFileComponent",
        version_component:"VersionComponent.VersionComponent",
        accessor_type_field:ComponentField.ComponentField["AccessorTypeComponent.AccessorTypeComponent"],
        arguments:dict[str,Any],
    ) -> None:
        self.version_file_component = version_file_component
        self.version_component = version_component
        self.accessor_type_field = accessor_type_field
        self.arguments = arguments
        self.accessor:Accessor.Accessor|None = None

    def create_accessor(self) -> Accessor.Accessor:
        if self.accessor is None:
            self.accessor = self.accessor_type_field.get_component().get_final().create_accessor(
                version=self.version_component.get_final(),
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

    def __init__(self, data: ComponentTyping.AccessorTypedDict, name: str, component_group: str, index: int | None) -> None:
        super().__init__(data, name, component_group, index)

        self.arguments = data["arguments"]

        self.accessor_type_field = ComponentField.ComponentField(data["accessor_type"], ACCESSOR_TYPE_PATTERN, ["accessor_type"], allow_inline=Field.InlinePermissions.reference)
        self.fields.extend([self.accessor_type_field])

    def create_final(self) -> None:
        super().create_final()
        version_file = self.get_inline_parent()
        self.final = AccessorCreator(cast("VersionFileComponent.VersionFileComponent", self.get_inline_parent()), cast("VersionComponent.VersionComponent", version_file.get_inline_parent()), self.accessor_type_field, self.arguments)

    def check(self) -> list[Exception]:
        exceptions = super().check()
        trace = TypeVerifier.make_trace([self.name, self.component_group])
        exceptions.extend(self.accessor_type_field.get_component().get_final().get_parameters().verify(self.arguments, trace))
        return exceptions

    def finalize(self) -> None:
        super().finalize()
        final = self.get_final()
        final.create_accessor()
        final.clear_variables()

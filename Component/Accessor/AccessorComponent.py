from typing import TYPE_CHECKING, cast

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Downloader.Accessor as Accessor
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
from Utilities.FunctionCaller import WaitValue

if TYPE_CHECKING:
    import Component.Accessor.AccessorTypeComponent as AccessorTypeComponent
    import Component.Version.VersionComponent as VersionComponent
    import Component.Version.VersionFileComponent as VersionFileComponent

ACCESSOR_TYPE_PATTERN:Pattern.Pattern["AccessorTypeComponent.AccessorTypeComponent"] = Pattern.Pattern([{"is_accessor_type": True}])

class AccessorComponent(Component.Component[WaitValue[Accessor.Accessor]]):

    class_name = "Accessor"
    class_name_article = "an Accessor"
    my_capabilities = Capabilities.Capabilities(is_accessor=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("accessor_type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("arguments", "a dict", True, dict),
    )

    def __init__(self, data: ComponentTyping.AccessorTypedDict, name: str, component_group: str, index: int | None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.arguments = data["arguments"]

        self.accessor_type_field = ComponentField.ComponentField(data["accessor_type"], ACCESSOR_TYPE_PATTERN, ["accessor_type"], allow_inline=Field.InlinePermissions.reference)
        self.fields.extend([self.accessor_type_field])

    def create_accessor(self) -> Accessor.Accessor:
        version_file = cast("VersionFileComponent.VersionFileComponent", self.get_inline_parent())
        version = cast("VersionComponent.VersionComponent", version_file.get_inline_parent())
        output = self.accessor_type_field.get_component().get_final().create_accessor(
            version=version.get_final(),
            file_type=version_file.version_file_type_field.get_component().get_final(),
            accessor_arguments=self.arguments
        )
        output.initialize()
        return output

    def create_final(self) -> None:
        super().create_final()
        self.final = WaitValue(self.create_accessor)
    
    def check(self) -> list[Exception]:
        exceptions = super().check()
        trace = TypeVerifier.make_trace([self.name, self.component_group])
        exceptions.extend(self.accessor_type_field.get_component().get_final().get_parameters().verify(self.arguments, trace))
        return exceptions

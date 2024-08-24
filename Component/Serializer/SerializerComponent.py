import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Serializer.Field.SerializerTypeField as SerializerTypeField
import Serializer.Serializer as Serializer
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class SerializerComponent(Component.Component[Serializer.Serializer]):
    
    class_name = "Serializer"
    class_name_article = "a Serializer"
    my_capabilities = Capabilities.Capabilities(is_serializer=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("serializer_class", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    def __init__(self, data:ComponentTyping.SerializerTypedDict, name: str, component_group: str, index: int | None) -> None:
        super().__init__(data, name, component_group, index)

        self.arguments = data.get("arguments", {})
        
        self.serializer_class_field = SerializerTypeField.SerializerTypeField(data["serializer_class"], ["serializer_class"])
        self.fields.extend([self.serializer_class_field])

    def link_finals(self) -> list[Exception]:
        return super().link_finals()

    def create_final(self) -> None:
        super().create_final()
        self.final = self.serializer_class_field.get_final()(**self.arguments)

    def check(self) -> list[Exception]:
        exceptions = super().check()
        trace = TypeVerifier.make_trace([self.name, self.component_group])
        exceptions.extend(self.serializer_class_field.get_final().type_verifier.verify(self.arguments, trace))
        return exceptions

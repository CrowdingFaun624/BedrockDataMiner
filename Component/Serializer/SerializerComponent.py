import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.LinkedObjectsField as LinkedObjectsField
import Component.Pattern as Pattern
import Component.Serializer.Field.SerializerTypeField as SerializerTypeField
import Serializer.Serializer as Serializer
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

SERIALIZER_PATTERN:Pattern.Pattern["SerializerComponent"] = Pattern.Pattern([{"is_serializer": True}])

class SerializerComponent(Component.Component[Serializer.Serializer]):

    class_name = "Serializer"
    class_name_article = "a Serializer"
    my_capabilities = Capabilities.Capabilities(is_serializer=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("linked_serializers", "a dict of strs", False, TypeVerifier.DictTypeVerifier(dict, str, str, "a dict", "a str", "a str")),
        TypeVerifier.TypedDictKeyTypeVerifier("serializer_class", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    __slots__ = (
        "arguments",
        "linked_serializers_field",
        "serializer_class_field",
    )

    def initialize_fields(self, data: ComponentTyping.SerializerTypedDict) -> list[Field.Field]:
        self.arguments = data.get("arguments", {})

        self.serializer_class_field = SerializerTypeField.SerializerTypeField(data["serializer_class"], self.domain, ["serializer_class"])
        self.linked_serializers_field = LinkedObjectsField.LinkedObjectsField(data.get("linked_serializers", {}), SERIALIZER_PATTERN, ["linked_serializers"])

        return [self.serializer_class_field, self.linked_serializers_field]

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        exceptions.extend(self.linked_serializers_field.check_coverage(lambda component: component.get_final(), self.get_final().linked_serializers, self))
        linked_serializers = dict(self.linked_serializers_field.map(lambda key, component: component.get_final()))
        self.get_final().link_finals(
            linked_serializers=linked_serializers,
        )
        return exceptions

    def create_final(self) -> None:
        super().create_final()
        self.final = self.serializer_class_field.get_final()(self.name, self.domain, **self.arguments)

    def check(self) -> list[Exception]:
        exceptions = super().check()
        trace = TypeVerifier.make_trace([self.name, self.component_group])
        exceptions.extend(self.serializer_class_field.get_final().type_verifier.verify(self.arguments, trace))
        return exceptions

    def finalize(self) -> list[Exception]:
        exceptions = super().finalize()
        self.get_final().finalize()
        return exceptions

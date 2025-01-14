import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.LinkedObjectsField as LinkedObjectsField
import Component.Field.ScriptedClassField as ScriptedClassField
import Component.Pattern as Pattern
import Serializer.Serializer as Serializer
import Utilities.TypeVerifier as TypeVerifier

SERIALIZER_PATTERN:Pattern.Pattern["SerializerComponent"] = Pattern.Pattern("is_serializer")

class SerializerComponent(Component.Component[Serializer.Serializer]):

    class_name = "Serializer"
    my_capabilities = Capabilities.Capabilities(is_serializer=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("linked_serializers", False, TypeVerifier.DictTypeVerifier(dict, str, str)),
        TypeVerifier.TypedDictKeyTypeVerifier("serializer_class", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "arguments",
        "linked_serializers_field",
        "serializer_class_field",
    )

    def initialize_fields(self, data: ComponentTyping.SerializerTypedDict) -> list[Field.Field]:
        self.arguments = data.get("arguments", {})

        self.serializer_class_field = ScriptedClassField.ScriptedClassField(data["serializer_class"], lambda script_set_set_set: script_set_set_set.serializer_classes, ["serializer_class"])
        self.linked_serializers_field = LinkedObjectsField.LinkedObjectsField(data.get("linked_serializers", {}), SERIALIZER_PATTERN, ["linked_serializers"], allow_inline=Field.InlinePermissions.reference, assume_component_group="serializers")

        return [self.serializer_class_field, self.linked_serializers_field]

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        exceptions.extend(self.linked_serializers_field.check_coverage(lambda component: component.final, self.final.linked_serializers, self))
        linked_serializers = dict(self.linked_serializers_field.map(lambda key, component: component.final))
        self.final.link_finals(
            linked_serializers=linked_serializers,
        )
        return exceptions

    def create_final(self) -> Serializer.Serializer:
        return self.serializer_class_field.object_class(self.name, self.domain, **self.arguments)

    def check(self) -> list[Exception]:
        exceptions = super().check()
        trace = TypeVerifier.make_trace([self.name, self.component_group])
        exceptions.extend(self.serializer_class_field.object_class.type_verifier.verify(self.arguments, trace))
        return exceptions

    def finalize(self) -> list[Exception]:
        exceptions = super().finalize()
        self.final.finalize()
        return exceptions

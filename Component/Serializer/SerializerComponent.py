from typing import Sequence

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.ScriptedClassField as ScriptedClassField
import Component.Pattern as Pattern
import Serializer.Serializer as Serializer
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

SERIALIZER_PATTERN:Pattern.Pattern["SerializerComponent"] = Pattern.Pattern("is_serializer")

class SerializerComponent(Component.Component[Serializer.Serializer]):

    class_name = "Serializer"
    my_capabilities = Capabilities.Capabilities(is_serializer=True)
    script_referenceable = True
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("serializer_class", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "arguments",
        "serializer_class_field",
    )

    def initialize_fields(self, data: ComponentTyping.SerializerTypedDict) -> Sequence[Field.Field]:
        self.arguments = data.get("arguments", {})

        self.serializer_class_field = ScriptedClassField.ScriptedClassField(data["serializer_class"], lambda script_set_set_set: script_set_set_set.serializer_classes, ("serializer_class",))

        return (self.serializer_class_field,)

    def create_final(self, trace:Trace.Trace) -> Serializer.Serializer:
        return self.serializer_class_field.object_class(self.name, self.domain, **self.arguments)

    def check(self, trace:Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().check(trace)
            self.serializer_class_field.object_class.type_verifier.verify(self.arguments, trace)

    def finalize(self, trace:Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().finalize(trace)
            self.final.finalize()
